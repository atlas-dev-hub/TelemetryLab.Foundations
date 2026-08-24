#!/usr/bin/env python3
"""
A reference solution for Module 4, kept out of the learner's way.

Deliberately Python and deliberately not sharing a line with the Node reference
consumer in `consumer/`. If the validator only ever passed one implementation,
"write your own consumer" would really mean "reproduce ours" — this exists to
prove a genuinely independent one can satisfy the contract, in a different
language, with a different Kafka client.

It is also the fixture the lab's own tests run, so a change that quietly makes
Module 4 unpassable fails here first.
"""

from __future__ import annotations

import json
import os
import sys
from collections import defaultdict

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "producer", "_generated"),
)

from confluent_kafka import Consumer  # noqa: E402
from ma.streaming.open_data.v1 import open_data_pb2  # noqa: E402

BOOTSTRAP = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")
DATA_TOPIC = "Data.Default.Stream1"
ESSENTIALS_TOPIC = "Essentials.Default"
SESSION_TOPIC = "System.SessionInfo"
OUT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "my-consumer.json"
)


def drain(topic: str, idle_s: float = 6.0) -> list:
    """Read a topic from the beginning until it goes quiet."""
    import time

    c = Consumer(
        {
            "bootstrap.servers": BOOTSTRAP,
            "group.id": f"module4-{topic}-{time.time_ns()}",
            "auto.offset.reset": "earliest",
            "enable.auto.commit": False,
        }
    )
    c.subscribe([topic])
    packets = []
    last = time.time()
    while time.time() - last < idle_s:
        msg = c.poll(1.0)
        if msg is None or msg.error():
            continue
        last = time.time()
        p = open_data_pb2.Packet()
        try:
            p.ParseFromString(msg.value())
        except Exception:  # noqa: BLE001
            continue
        packets.append(p)
    c.close()
    return packets


def main() -> int:
    units: dict[str, str] = {}
    fmt_to_param: dict[int, str] = {}

    # Configuration first. Kafka orders within a partition, not across topics,
    # so reading data before the definitions that explain it loses everything.
    for p in drain(ESSENTIALS_TOPIC, idle_s=4.0):
        if p.type == "Configuration":
            c = open_data_pb2.ConfigurationPacket()
            c.ParseFromString(p.content)
            for d in c.parameter_definitions:
                units[d.identifier] = d.units
        elif p.type == "DataFormatDefinition":
            d = open_data_pb2.DataFormatDefinitionPacket()
            d.ParseFromString(p.content)
            ids = list(d.parameter_identifiers.parameter_identifiers)
            if ids:
                fmt_to_param[d.identifier] = ids[0]

    samples: dict[str, int] = defaultdict(int)
    laps = 0
    session = ""
    latest_session_key = None

    # The session's identifier is NOT on the data stream. The producer writes a
    # bare NewSessionPacket there; it is the Stream API that publishes an
    # enriched one, carrying session_info, to System.SessionInfo.
    for p in drain(SESSION_TOPIC, idle_s=4.0):
        if p.type == "NewSession":
            n = open_data_pb2.NewSessionPacket()
            n.ParseFromString(p.content)
            if n.HasField("session_info") and n.session_info.identifier:
                session = n.session_info.identifier
                latest_session_key = p.session_key

    data = drain(DATA_TOPIC, idle_s=6.0)

    for p in data:
        if latest_session_key and p.session_key != latest_session_key:
            continue
        if p.type == "PeriodicData":
            d = open_data_pb2.PeriodicDataPacket()
            d.ParseFromString(p.content)
            ident = fmt_to_param.get(d.data_format.data_format_identifier)
            if ident is None:
                continue
            for col in d.columns:
                samples[ident] += len(col.double_samples.samples)
        elif p.type == "Marker":
            m = open_data_pb2.MarkerPacket()
            m.ParseFromString(p.content)
            if m.type == "Lap Trigger":
                laps += 1

    out = {
        "sessionIdentifier": session,
        "channels": [
            {"identifier": ident, "units": units.get(ident, ""), "samples": n}
            for ident, n in sorted(samples.items())
        ],
        "lapMarkers": laps,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)

    print(f"{len(out['channels'])} channels, {sum(samples.values())} samples, {laps} lap markers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
