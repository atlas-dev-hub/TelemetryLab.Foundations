"""
Writing telemetry into ATLAS Open Streaming.

Producers talk gRPC to the Stream API. They never write to Kafka directly -
doing that skips session and data-format registration, and ATLAS will never
see the data even though the bytes are sitting in the topic.

The order below is not stylistic. Each rule here was learned by something
silently not working:

  1. CreateSession, then NewSessionPacket, then a pause, then configuration,
     then data-format registration, then data. Out of order, packets are
     dropped without an error.
  2. One parameter per data format and one parameter per PeriodicDataPacket.
     Bundling several parameters behind one format id does not work.
  3. Exactly ONE GroupDefinition - but not for the reason usually given.
     Tested against this stack, a ConfigurationPacket carrying two groups is
     accepted by the Stream API and every sample reaches Kafka and reads back
     correctly. The constraint is reported *downstream*, in ATLAS / SQL Race,
     which will not render the session. We have not been able to verify the
     ATLAS side here (it needs a licensed Windows install), so treat this as
     "one group, because ATLAS compatibility depends on it" rather than
     "the Stream API will reject it". The distinction matters when you are
     debugging: the packets being in Kafka does *not* mean you are fine.
  4. Configuration must go to BOTH the data stream and the main stream (""),
     marked essential. SQL Race needs it on every stream it writes to, and a
     stream without it ignores everything that follows.
  5. Timestamps must be contiguous - each batch starts where the last ended.
     Gaps produce discontinuous traces.
  6. Everything is nanoseconds: start_time, interval, marker timestamps.
"""

from __future__ import annotations

import logging
import os
import sys
import time

import grpc

_GENERATED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "_generated")
if _GENERATED not in sys.path:
    sys.path.insert(0, os.path.normpath(_GENERATED))

from ma.streaming.api.v1 import api_pb2, api_pb2_grpc  # noqa: E402
from ma.streaming.key_generator.v1 import (  # noqa: E402
    key_generator_pb2,
    key_generator_pb2_grpc,
)
from ma.streaming.open_data.v1 import open_data_pb2  # noqa: E402

from .channels import APPLICATION, GROUP, ChannelDef  # noqa: E402

logger = logging.getLogger(__name__)

DATA_SOURCE = "Default"
DATA_STREAM = "Stream1"
MAIN_STREAM = ""  # the empty string is the main stream, not a missing value


def _packet_type(obj) -> str:
    n = obj.__class__.__name__
    return n[:-6] if n.endswith("Packet") else n


class AtlasWriter:
    def __init__(
        self,
        stream_api_address: str | None = None,
        key_generator_address: str | None = None,
        data_source: str = DATA_SOURCE,
        stream: str = DATA_STREAM,
    ) -> None:
        self.stream_api_address = stream_api_address or os.environ.get(
            "STREAM_API_ADDRESS", "localhost:13579"
        )
        self.key_generator_address = key_generator_address or os.environ.get(
            "KEY_GENERATOR_ADDRESS", "localhost:15379"
        )
        self.data_source = data_source
        self.stream = stream

        self._channel = None
        self._keygen_channel = None
        self._session_key: str | None = None
        self._data_format_ids: dict[str, int] = {}
        self._channels: tuple[ChannelDef, ...] = ()
        self._next_packet_id = 0

    # --- connection ---------------------------------------------------------

    def connect(self, timeout_s: float = 30.0) -> None:
        deadline = time.time() + timeout_s
        last: Exception | None = None
        while time.time() < deadline:
            try:
                self._channel = grpc.insecure_channel(self.stream_api_address)
                self._session_stub = api_pb2_grpc.SessionManagementServiceStub(self._channel)
                self._dfmt_stub = api_pb2_grpc.DataFormatManagerServiceStub(self._channel)
                self._writer_stub = api_pb2_grpc.PacketWriterServiceStub(self._channel)

                self._keygen_channel = grpc.insecure_channel(self.key_generator_address)
                self._keygen_stub = key_generator_pb2_grpc.UniqueKeyGeneratorServiceStub(
                    self._keygen_channel
                )

                # Prove the connection rather than assuming it.
                self._session_stub.GetCurrentSessions(
                    api_pb2.GetCurrentSessionsRequest(data_source=self.data_source)
                )
                return
            except Exception as e:  # noqa: BLE001 - retry anything while starting
                last = e
                time.sleep(1.0)
        raise ConnectionError(
            f"Could not reach the Stream API at {self.stream_api_address} "
            f"within {timeout_s:.0f}s. Is the stack up? Last error: {last}"
        )

    def close(self) -> None:
        for ch in (self._keygen_channel, self._channel):
            if ch is not None:
                ch.close()
        self._channel = self._keygen_channel = None
        self._session_key = None

    # --- internals ----------------------------------------------------------

    def _new_key(self) -> str:
        return self._keygen_stub.GenerateUniqueKey(
            key_generator_pb2.GenerateUniqueKeyRequest(type=key_generator_pb2.KEY_TYPE_STRING)
        ).string_key

    def _write(self, payload: bytes, ptype: str, stream: str, essential: bool = False) -> None:
        message = open_data_pb2.Packet(
            type=ptype,
            content=payload,
            session_key=self._session_key,
            is_essential=essential,
            id=self._next_packet_id,
        )
        self._next_packet_id += 1
        self._writer_stub.WriteDataPacket(
            api_pb2.WriteDataPacketRequest(
                detail=api_pb2.DataPacketDetails(
                    message=message,
                    data_source=self.data_source,
                    stream=stream,
                    session_key=self._session_key,
                )
            )
        )

    # --- session lifecycle --------------------------------------------------

    def start_session(self, identifier: str, channels: tuple[ChannelDef, ...]) -> str:
        self._channels = channels

        resp = self._session_stub.CreateSession(
            api_pb2.CreateSessionRequest(
                data_source=self.data_source,
                identifier=identifier,
                type="Session",
                version=1,
            )
        )
        self._session_key = resp.session_key

        new_session = open_data_pb2.NewSessionPacket(data_source=self.data_source)
        ptype = _packet_type(new_session)
        payload = new_session.SerializeToString()
        self._write(payload, ptype, self.stream)
        self._write(payload, ptype, MAIN_STREAM)

        # Rule 1: give the Stream API a moment to register the session before
        # configuration arrives. Without this the config can land first and be
        # discarded.
        time.sleep(1.0)

        config = open_data_pb2.ConfigurationPacket(
            config_id=self._new_key(),
            parameter_definitions=[
                open_data_pb2.ParameterDefinition(
                    identifier=c.identifier,
                    name=c.key,
                    application_name=APPLICATION,
                    description=c.description,
                    units=c.units,
                    data_type=open_data_pb2.DATA_TYPE_FLOAT64,
                    format_string=c.format_string,
                    min_value=c.min_value,
                    max_value=c.max_value,
                    frequencies=[c.frequency],
                    groups=[GROUP],
                )
                for c in channels
            ],
            # Rule 3: exactly one group. More than one is silently rejected.
            group_definitions=[
                open_data_pb2.GroupDefinition(
                    identifier=GROUP,
                    application_name=APPLICATION,
                    name=GROUP,
                    description="Synthetic GT3 car telemetry",
                )
            ],
        )
        payload = config.SerializeToString()
        ptype = _packet_type(config)
        # Rule 4: both streams, marked essential.
        self._write(payload, ptype, MAIN_STREAM, essential=True)
        self._write(payload, ptype, self.stream, essential=True)

        # Rule 2: one data format per parameter.
        self._data_format_ids = {
            c.identifier: self._dfmt_stub.GetParameterDataFormatId(
                api_pb2.GetParameterDataFormatIdRequest(
                    data_source=self.data_source, parameters=[c.identifier]
                )
            ).data_format_identifier
            for c in channels
        }

        return self._session_key

    def write_batch(
        self, batch: dict[str, list[float]], start_time_ns: int, interval_ns: int
    ) -> None:
        """Write one batch of samples. Rule 2: one packet per parameter."""
        for c in self._channels:
            values = batch.get(c.key)
            if not values:
                continue
            packet = open_data_pb2.PeriodicDataPacket(
                data_format=open_data_pb2.SampleDataFormat(
                    data_format_identifier=self._data_format_ids[c.identifier]
                ),
                start_time=start_time_ns,
                interval=interval_ns,
                columns=[
                    open_data_pb2.SampleColumn(
                        double_samples=open_data_pb2.DoubleSampleList(
                            samples=[
                                open_data_pb2.DoubleSample(
                                    value=v, status=open_data_pb2.DATA_STATUS_VALID
                                )
                                for v in values
                            ]
                        )
                    )
                ],
            )
            self._write(packet.SerializeToString(), _packet_type(packet), self.stream)

    def write_marker(
        self, timestamp_ns: int, label: str, marker_type: str, description: str, value: int
    ) -> None:
        marker = open_data_pb2.MarkerPacket(
            timestamp=timestamp_ns,
            label=label,
            type=marker_type,
            description=description,
            source="0",
            value=value,
        )
        payload = marker.SerializeToString()
        ptype = _packet_type(marker)
        # Markers go to both streams so the data stream has config context for
        # lap creation.
        self._write(payload, ptype, self.stream)
        self._write(payload, ptype, MAIN_STREAM)

    def end_session(self, timestamp_ns: int) -> None:
        if self._session_key is None:
            return
        end = open_data_pb2.EndOfSessionPacket(data_source=self.data_source)
        payload = end.SerializeToString()
        ptype = _packet_type(end)
        self._write(payload, ptype, self.stream)
        self._write(payload, ptype, MAIN_STREAM)
        try:
            self._session_stub.EndSession(
                api_pb2.EndSessionRequest(
                    data_source=self.data_source, session_key=self._session_key
                )
            )
        except Exception as e:  # noqa: BLE001
            logger.warning("EndSession call failed: %s", e)
