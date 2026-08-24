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
import random
import string
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAB = os.path.join(ROOT, ".lab")
CONSUMED = os.path.join(LAB, ".consumed")
MY_CONSUMER = os.path.join(LAB, "my-consumer.json")

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


def bash() -> str:
    """
    Resolve a usable bash.

    On Windows `which("bash")` typically finds the WSL shim, which cannot see
    the Windows filesystem the way the rest of the lab expects and fails with a
    baffling `execvpe(/bin/bash)` error. Git for Windows ships a real bash, so
    prefer that. CI is Linux and takes the first branch.
    """
    from shutil import which

    if os.name == "nt":
        for candidate in (
            r"C:\Program Files\Git\bin\bash.exe",
            r"C:\Program Files (x86)\Git\bin\bash.exe",
        ):
            if os.path.exists(candidate):
                return candidate
    found = which("bash")
    if found:
        return found
    raise Failed(
        "bash is not available.",
        "The lab runs `my-consumer/run.sh` with bash. On Windows, install Git "
        "for Windows (which includes it) or run the lab in the Codespace.",
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


def ground_truth(producer_output: str) -> dict:
    """
    What the producer says it sent.

    Grading a consumer against the producer's own record, rather than against
    the reference consumer, matters: two implementations can share the same
    misunderstanding and agree with each other while both being wrong. The
    producer is the only thing that knows for certain.
    """
    out: dict = {"channels": {}, "samples_per_channel": 0, "lap_markers": 0, "session": ""}
    for line in producer_output.splitlines():
        if line.startswith("LAB_SESSION="):
            out["session"] = line.split("=", 1)[1].strip()
        elif line.startswith("LAB_SAMPLES_PER_CHANNEL="):
            out["samples_per_channel"] = int(line.split("=", 1)[1])
        elif line.startswith("LAB_LAP_MARKERS="):
            out["lap_markers"] = int(line.split("=", 1)[1])
        elif line.startswith("LAB_CHANNELS="):
            for pair in line.split("=", 1)[1].split(","):
                name, _, units = pair.partition(":")
                if name:
                    out["channels"][name] = units
    return out


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


def module_4(handle: str) -> str:
    """Their own consumer, graded against what the producer actually sent."""
    wait_for_stream_api()

    # Vary the stream so a hardcoded answer cannot pass.
    #
    # A different number of laps, and one extra channel whose name and units are
    # invented here. A consumer that assumes eleven channels, or that has the
    # unit strings baked in, fails — which is the point: the whole argument for
    # a telemetry data model is that a consumer should not need to know these in
    # advance.
    rand = random.Random()
    laps = rand.randint(2, 4)
    extra_name = "Aux" + "".join(rand.choice(string.ascii_uppercase) for _ in range(4))
    extra_units = rand.choice(["bar", "degC", "kPa", "V", "rpm", "mm"])

    output = produce(["--laps", str(laps), "--extra-channel", f"{extra_name}:{extra_units}"])
    truth = ground_truth(output)

    if not truth.get("channels"):
        raise Failed(
            "The producer did not report what it sent.",
            "That is ours, not yours. Please raise an issue.",
        )

    if os.path.exists(MY_CONSUMER):
        os.remove(MY_CONSUMER)

    r = run([bash(), "my-consumer/run.sh"], timeout=600)
    if not os.path.exists(MY_CONSUMER):
        tail = (r.stdout or "") + (r.stderr or "")
        raise Failed(
            "`my-consumer/run.sh` did not produce `.lab/my-consumer.json`.",
            "It must read the stream and write that file. See "
            "`my-consumer/README.md` for the shape.\n\n"
            "What it printed:\n\n```\n" + tail.strip()[-1200:] + "\n```",
        )

    try:
        with open(MY_CONSUMER, encoding="utf-8") as f:
            got = json.load(f)
    except Exception as e:  # noqa: BLE001
        raise Failed(
            f"`.lab/my-consumer.json` is not valid JSON ({e}).",
            "See `my-consumer/README.md` for the expected shape.",
        )

    # --- compare against the producer's own record --------------------------
    expected_units = truth["channels"]
    got_channels = {
        str(c.get("identifier", "")).split(":", 1)[0]: c
        for c in got.get("channels", [])
        if isinstance(c, dict)
    }

    missing = sorted(set(expected_units) - set(got_channels))
    if missing:
        raise Failed(
            f"Your consumer reported {len(got_channels)} channels; the producer "
            f"sent {len(expected_units)}.",
            "Missing: " + ", ".join(f"`{m}`" for m in missing[:8]) + "\n\n"
            f"Note that this run included an extra channel, `{extra_name}`, that "
            "is not in the lab's default set. The validator invents one on every "
            "run — a consumer that assumes a fixed channel list will not pass.",
        )

    wrong_units = [
        (name, got_channels[name].get("units"), expected_units[name])
        for name in expected_units
        if str(got_channels[name].get("units", "")) != expected_units[name]
    ]
    if wrong_units:
        rows = "\n".join(
            f"- `{n}`: you reported `{g}`, the configuration said `{e}`"
            for n, g, e in wrong_units[:6]
        )
        raise Failed(
            f"{len(wrong_units)} channel(s) came back with the wrong units.",
            "Units are not something to infer or hardcode — they arrive in the "
            "`ConfigurationPacket`, per parameter.\n\n" + rows,
        )

    expected_samples = truth["samples_per_channel"]
    bad_counts = [
        (name, got_channels[name].get("samples"))
        for name in expected_units
        if int(got_channels[name].get("samples", -1) or 0) != expected_samples
    ]
    if bad_counts:
        rows = "\n".join(f"- `{n}`: you counted {c}" for n, c in bad_counts[:6])
        raise Failed(
            f"Sample counts do not match. The producer sent **{expected_samples}** "
            f"per channel; {len(bad_counts)} channel(s) disagree.",
            "Each `PeriodicDataPacket` carries one column of samples for one "
            "parameter. Count what you decode, not what you expect.\n\n" + rows,
        )

    if str(got.get("sessionIdentifier", "")) != truth["session"]:
        raise Failed(
            "The session identifier does not match.",
            f"You reported `{got.get('sessionIdentifier')}`.\n"
            f"The producer created `{truth['session']}`.",
        )

    if int(got.get("lapMarkers", -1) or 0) != truth["lap_markers"]:
        raise Failed(
            f"Lap markers: you reported {got.get('lapMarkers')}, "
            f"there were {truth['lap_markers']}.",
            "Count `MarkerPacket`s whose `type` is `Lap Trigger`. This run had "
            f"{laps} laps plus the out lap.",
        )

    return (
        "Your consumer decoded the stream correctly, on a session it had never "
        "seen before.\n\n"
        f"- Channels: **{len(expected_units)}** — including `{extra_name}` "
        f"(`{extra_units}`), invented for this run\n"
        f"- Samples per channel: **{expected_samples:,}**\n"
        f"- Laps: {laps} plus the out lap\n\n"
        "Nothing about this run was knowable in advance. The channel list, its "
        "units and the lap count all came out of the stream itself — which is "
        "exactly what a telemetry data model is for, and what you would have had "
        "to maintain by hand on a bare topic."
    )


MODULES[4] = ("Write your first consumer", module_4)


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
