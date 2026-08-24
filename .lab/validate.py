#!/usr/bin/env python3
"""
Validate one module.

    python .lab/validate.py <module-number> [--handle <github-handle>]

Writes a markdown report to stdout — the workflow posts it verbatim as a PR
comment — and exits 0 on pass, 1 on fail.

Two rules this file lives by:

  1. **Grade behaviour, not shape.** Never assert on file contents or the
     presence of a line. Run the thing and check what it did. A learner who
     solves a module a different way than we expected should still pass.
  2. **Failures teach.** A red X tells someone they are wrong. It does not tell
     them what to do. Most of the value here is in the failure text.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, ".lab")
CONSUMED = os.path.join(LAB, ".consumed")

STREAM_API = os.environ.get("STREAM_API_ADDRESS", "localhost:13579")
KAFKA = os.environ.get("KAFKA_BOOTSTRAP", "localhost:9092")

# The eleven channels the lab ships with. Module 2 asks for one that is not here.
SHIPPED = {
    "Speed", "Throttle", "Brake", "Gear", "RPM", "SteeringAngle",
    "LatAccel", "LongAccel", "Yaw", "LapDistance", "LapNumber",
}


class Failed(Exception):
    def __init__(self, problem: str, fix: str = "") -> None:
        super().__init__(problem)
        self.problem = problem
        self.fix = fix


# --- helpers ----------------------------------------------------------------


def run(cmd: list[str], cwd: str | None = None, timeout: int = 600) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd, cwd=cwd or ROOT, capture_output=True, text=True, timeout=timeout
    )


def wait_for_stream_api(timeout_s: float = 90) -> None:
    """The container is running a few seconds before gRPC is accepting."""
    sys.path.insert(0, os.path.join(ROOT, "producer", "_generated"))
    import grpc
    from ma.streaming.api.v1 import api_pb2, api_pb2_grpc

    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        try:
            ch = grpc.insecure_channel(STREAM_API)
            stub = api_pb2_grpc.SessionManagementServiceStub(ch)
            stub.GetCurrentSessions(
                api_pb2.GetCurrentSessionsRequest(data_source="Default"), timeout=5
            )
            ch.close()
            return
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(2)
    raise Failed(
        f"The Stream API at {STREAM_API} never came up ({type(last).__name__}).",
        "This is almost always the stack, not your code. Check the workflow log "
        "for the `docker compose up` step.",
    )


def produce(extra: list[str] | None = None, script: str = "produce.py") -> str:
    """Run a producer. Returns its stdout."""
    cmd = [sys.executable, script, "--laps", "1", "--fast"] + (extra or [])
    r = run(cmd, cwd=os.path.join(ROOT, "producer"))
    if r.returncode != 0:
        tail = (r.stderr or r.stdout).strip().splitlines()[-12:]
        raise Failed(
            "The producer did not run.",
            "It exited with an error before streaming anything:\n\n```\n"
            + "\n".join(tail)
            + "\n```",
        )
    return r.stdout


def npm() -> str:
    """
    Resolve npm properly.

    On Windows npm is `npm.cmd`, and subprocess without a shell will not find a
    bare "npm". CI is Linux so this would never have surfaced there - but
    learners run these checks on their own machines, where a cryptic
    FileNotFoundError is exactly the kind of thing that makes someone give up.
    """
    from shutil import which

    for candidate in ("npm", "npm.cmd"):
        found = which(candidate)
        if found:
            return found
    raise Failed(
        "npm is not installed, or not on PATH.",
        "The consumer is a Node project. Install Node 20 or later and try again.",
    )


def consume() -> dict:
    """Run the consumer and return what it recovered."""
    if os.path.exists(CONSUMED):
        os.remove(CONSUMED)
    r = run([npm(), "start", "--silent"], cwd=os.path.join(ROOT, "consumer"), timeout=300)
    if not os.path.exists(CONSUMED):
        tail = (r.stderr or r.stdout).strip().splitlines()[-12:]
        raise Failed(
            "The consumer did not read anything back.",
            "```\n" + "\n".join(tail) + "\n```",
        )
    with open(CONSUMED, encoding="utf-8") as f:
        return json.load(f)


def session_identifier(producer_output: str) -> str | None:
    """
    The identifier of the session the producer just created.

    Deliberately not via GetCurrentSessions: that returns *live* sessions, and a
    well-behaved producer closes its session when it finishes, so by the time we
    look there is nothing current. The producer prints the identifier only after
    a successful CreateSession round-trip, which makes the line evidence rather
    than a claim - and topic_counts() below independently confirms the data
    actually landed.
    """
    for line in producer_output.splitlines():
        if line.startswith("LAB_SESSION="):
            return line.split("=", 1)[1].strip()
    return None


def topic_counts() -> dict[str, int]:
    """Message count per Kafka topic, via the broker's own CLI."""
    r = run(
        ["docker", "compose", "exec", "-T", "kafka",
         "/opt/kafka/bin/kafka-get-offsets.sh", "--bootstrap-server", "localhost:9092"],
        timeout=120,
    )
    counts: dict[str, int] = {}
    for line in r.stdout.splitlines():
        parts = line.strip().split(":")
        if len(parts) == 3 and parts[2].isdigit():
            counts[parts[0]] = counts.get(parts[0], 0) + int(parts[2])
    return counts


# --- the modules ------------------------------------------------------------


def module_1(handle: str) -> str:
    """Run the pipeline, and make the session yours."""
    wait_for_stream_api()
    output = produce()
    identifier = session_identifier(output)

    if not identifier:
        raise Failed(
            "The producer ran, but never reported creating a session.",
            "A session is created before any samples are sent. If none appeared, "
            "the producer could not reach the Stream API. Check the "
            "`docker compose up` step in the workflow log.",
        )

    if handle.lower() not in identifier.lower():
        raise Failed(
            f"A session was created, but it does not carry your handle (`{handle}`).",
            "Open `producer/produce.py` and set `LAB_HANDLE` to your GitHub "
            f"handle — `{handle}`.\n\n"
            f"The session identifier was:\n\n```\n{identifier}\n```",
        )

    counts = topic_counts()
    samples = counts.get("Data.Default.Stream1", 0)
    if samples == 0:
        raise Failed(
            "The session was named correctly, but no telemetry reached Kafka.",
            "The session lifecycle worked and the data path did not. Check the "
            "producer output in the workflow log for errors after the "
            "configuration step.",
        )

    return (
        "The stack came up, the producer streamed a lap through the Stream API "
        "into Kafka, and the session carries your handle.\n\n"
        f"- Session: `{identifier}`\n"
        f"- Telemetry messages in Kafka: **{samples:,}**\n"
        f"- Configuration messages: {counts.get('Essentials.Default', 0)}\n\n"
        "That identifier travels with every packet. A session is not an "
        "anonymous window of time — it has an identity, and you just set it."
    )


def module_2(handle: str) -> str:
    """Add a channel, and see the consumer learn about it without being told."""
    wait_for_stream_api()
    produce()
    recovered = consume()

    names = {c.split(":", 1)[0] for c in recovered.get("channels", [])}
    added = names - SHIPPED

    if not added:
        raise Failed(
            "Only the eleven channels the lab ships with are on the stream.",
            "Two edits are needed, and the second is the one people forget:\n\n"
            "1. Add a `ChannelDef` to `producer/atlas_lab/channels.py`\n"
            "2. Emit a value for it from `step()` in `producer/atlas_lab/lapsim.py`\n\n"
            "A declaration with nothing producing values for it is a channel "
            "that exists and is always empty.",
        )

    return (
        f"New channel on the stream: **{', '.join(sorted(added))}**\n\n"
        f"- Channels recovered: {len(recovered.get('channels', []))}\n"
        f"- Samples: {recovered.get('samples', 0):,}\n\n"
        "The consumer was not modified and does not know your channel exists. "
        "It learned the name, the units and the range from the configuration "
        "packet, in-band, at runtime. That is the thing a bare Kafka topic "
        "cannot do for you."
    )


def module_3(handle: str) -> str:
    """Find and fix the timestamp bug in the variant producer."""
    wait_for_stream_api()
    produce(script="produce_v2.py")
    recovered = consume()

    gaps = recovered.get("timestampGaps")
    if gaps is None:
        raise Failed(
            "The consumer did not report on timestamp continuity.",
            "This one is ours - the consumer should always report it. Please "
            "raise an issue.",
        )

    if gaps > 0:
        worst_ms = recovered.get("worstGapNs", 0) / 1e6
        raise Failed(
            f"`produce_v2.py` still leaves **{gaps} discontinuities** in the "
            f"timeline (worst: {worst_ms:.1f} ms).",
            "Every sample is present and every value is correct — what is "
            "wrong is *when they claim to have happened*.\n\n"
            "A `PeriodicDataPacket` declares a start time and an interval. That "
            "means the next packet for a channel has to start exactly one "
            "interval after the previous packet's last sample. Look at what "
            "happens to `timestamp_ns` after each batch is written, and ask "
            "where the value for the *next* batch comes from.\n\n"
            "Compare it against `produce.py`, which is correct."
        )

    return (
        "`produce_v2.py` now produces a contiguous timeline — every batch "
        "starts exactly where the previous one ended.\n\n"
        "- Discontinuities: **0**\n"
        f"- Samples: {recovered.get('samples', 0):,}\n\n"
        "The bug was that the producer asked the clock what time it was for each "
        "batch, instead of advancing its own count of how much data it had sent. "
        "Reading the clock measures *when the send happened*, which includes "
        "however long serialising and transmitting took. Measurement time and "
        "arrival time are different facts, and a recording that confuses them "
        "cannot be trusted later — the values are right, the moments are "
        "wrong, and nothing errors."
    )


MODULES = {
    1: ("Make it yours", module_1),
    2: ("Add a channel", module_2),
    3: ("Fix the broken producer", module_3),
}


# --- entry point ------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("module", type=int)
    ap.add_argument("--handle", default=os.environ.get("LAB_HANDLE", ""))
    args = ap.parse_args()

    if args.module not in MODULES:
        print(f"No module {args.module}.")
        return 2

    title, fn = MODULES[args.module]
    print(f"## Module {args.module} — {title}\n")

    try:
        detail = fn(args.handle)
    except Failed as e:
        print(f"### Not yet\n\n{e.problem}\n")
        if e.fix:
            print(f"{e.fix}\n")
        print("---\n\nPush another commit to this branch and it will re-run.")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"### Something went wrong\n\n`{type(e).__name__}: {e}`\n")
        print("This one is probably ours, not yours. Check the workflow log.")
        return 1

    print(f"### Passed\n\n{detail}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
