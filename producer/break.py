#!/usr/bin/env python3
"""
Break the pipeline on purpose.

    python break.py --list
    python break.py two-groups
    python break.py no-config
    python break.py late-config

Every failure mode here is one that produces **no error**. The producer reports
success, the packets are accepted, and the data simply never becomes readable.
Those are the expensive ones - an exception you can search for; silence you
cannot.

Run each, then run the consumer and see what happened to the data.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

from atlas_lab.channels import APPLICATION, CHANNELS, GROUP
from atlas_lab.lapsim import LapSimulator
from atlas_lab.writer import MAIN_STREAM, AtlasWriter, _packet_type

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "_generated"))
from ma.streaming.api.v1 import api_pb2  # noqa: E402
from ma.streaming.open_data.v1 import open_data_pb2  # noqa: E402

EVIDENCE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "lab", ".broken")

EXPERIMENTS = {
    "two-groups": "Send a ConfigurationPacket with TWO GroupDefinitions.",
    "no-config": "Send samples without ever sending a ConfigurationPacket.",
    "late-config": "Send samples first, configuration afterwards.",
}


def _stream_some_data(writer: AtlasWriter, seconds: float = 3.0, rate: int = 60) -> int:
    """Stream a few seconds of real telemetry, whatever state the session is in."""
    sim = LapSimulator(rate_hz=rate)
    interval_ns = int(1e9 / rate)
    timestamp_ns = time.time_ns()
    batch: dict[str, list[float]] = {c.key: [] for c in CHANNELS}
    sent = 0
    for _ in range(int(seconds * rate)):
        values, _crossed = sim.step()
        for k, v in values.items():
            if k in batch:
                batch[k].append(v)
        if len(batch[CHANNELS[0].key]) >= 6:
            writer.write_batch(batch, timestamp_ns, interval_ns)
            n = len(batch[CHANNELS[0].key])
            timestamp_ns += n * interval_ns
            sent += n
            batch = {c.key: [] for c in CHANNELS}
    return sent


def _minimal_session(writer: AtlasWriter, identifier: str) -> None:
    """CreateSession + NewSessionPacket, and nothing else."""
    resp = writer._session_stub.CreateSession(
        api_pb2.CreateSessionRequest(
            data_source=writer.data_source, identifier=identifier, type="Session", version=1
        )
    )
    writer._session_key = resp.session_key
    pkt = open_data_pb2.NewSessionPacket(data_source=writer.data_source)
    payload = pkt.SerializeToString()
    writer._write(payload, _packet_type(pkt), writer.stream)
    writer._write(payload, _packet_type(pkt), MAIN_STREAM)
    time.sleep(1.0)


def _config_packet(writer: AtlasWriter, group_count: int) -> open_data_pb2.ConfigurationPacket:
    groups = [
        open_data_pb2.GroupDefinition(
            identifier=GROUP,
            application_name=APPLICATION,
            name=GROUP,
            description="Synthetic GT3 car telemetry",
        )
    ]
    if group_count > 1:
        groups.append(
            open_data_pb2.GroupDefinition(
                identifier="Extra",
                application_name=APPLICATION,
                name="Extra",
                description="A perfectly reasonable second group",
            )
        )
    return open_data_pb2.ConfigurationPacket(
        config_id=writer._new_key(),
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
            for c in CHANNELS
        ],
        group_definitions=groups,
    )


def _register_formats(writer: AtlasWriter) -> None:
    writer._channels = CHANNELS
    writer._data_format_ids = {
        c.identifier: writer._dfmt_stub.GetParameterDataFormatId(
            api_pb2.GetParameterDataFormatIdRequest(
                data_source=writer.data_source, parameters=[c.identifier]
            )
        ).data_format_identifier
        for c in CHANNELS
    }


def run_two_groups(writer: AtlasWriter) -> str:
    _minimal_session(writer, f"BROKEN two-groups {time.strftime('%H:%M:%S')}")
    config = _config_packet(writer, group_count=2)
    payload = config.SerializeToString()
    ptype = _packet_type(config)
    writer._write(payload, ptype, MAIN_STREAM, essential=True)
    writer._write(payload, ptype, writer.stream, essential=True)
    _register_formats(writer)
    sent = _stream_some_data(writer)
    writer.end_session(time.time_ns())
    return f"sent {sent} samples with a two-group configuration"


def run_no_config(writer: AtlasWriter) -> str:
    _minimal_session(writer, f"BROKEN no-config {time.strftime('%H:%M:%S')}")
    # Formats still register - the Stream API is happy to allocate them. It is
    # the *consumer* that has no way to interpret what arrives.
    _register_formats(writer)
    sent = _stream_some_data(writer)
    writer.end_session(time.time_ns())
    return f"sent {sent} samples with no configuration at all"


def run_late_config(writer: AtlasWriter) -> str:
    _minimal_session(writer, f"BROKEN late-config {time.strftime('%H:%M:%S')}")
    _register_formats(writer)
    sent = _stream_some_data(writer, seconds=2.0)
    config = _config_packet(writer, group_count=1)
    payload = config.SerializeToString()
    ptype = _packet_type(config)
    writer._write(payload, ptype, MAIN_STREAM, essential=True)
    writer._write(payload, ptype, writer.stream, essential=True)
    sent += _stream_some_data(writer, seconds=2.0)
    writer.end_session(time.time_ns())
    return f"sent {sent} samples, configuration halfway through"


RUNNERS = {
    "two-groups": run_two_groups,
    "no-config": run_no_config,
    "late-config": run_late_config,
}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("experiment", nargs="?", choices=sorted(RUNNERS))
    p.add_argument("--list", action="store_true")
    args = p.parse_args()

    if args.list or not args.experiment:
        print("\nExperiments:\n")
        for k, v in EXPERIMENTS.items():
            print(f"  {k:<14} {v}")
        print("\nRun one, then run the consumer and see what survived.\n")
        return 0

    writer = AtlasWriter()
    print(f"Connecting to {writer.stream_api_address} ...")
    writer.connect()

    print(f"\nRunning experiment: {args.experiment}")
    print(f"  {EXPERIMENTS[args.experiment]}\n")
    result = RUNNERS[args.experiment](writer)
    writer.close()

    print(f"  Producer reported success: {result}.")
    print("  No error was raised. That is the point.\n")
    print("  Now run the consumer and count how many of those samples came back:")
    print("    cd ../consumer && npm start\n")

    done = {}
    if os.path.exists(EVIDENCE):
        try:
            with open(EVIDENCE, encoding="utf-8") as f:
                done = json.load(f)
        except Exception:  # noqa: BLE001
            done = {}
    done[args.experiment] = result
    os.makedirs(os.path.dirname(EVIDENCE), exist_ok=True)
    with open(EVIDENCE, "w", encoding="utf-8") as f:
        json.dump(done, f, indent=1)

    return 0


if __name__ == "__main__":
    sys.exit(main())
