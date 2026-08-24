#!/usr/bin/env python3
"""
A colleague's variant of the producer. Something is wrong with it.

The traces it produces look jumpy — speed appears to jerk backwards and
forwards even though the car is doing nothing unusual. All the samples are
there. None of them are missing. The values are identical to the ones
produce.py generates.

Your job in Module 3 is to work out why, and fix it.

Run it and then run the consumer. The consumer will tell you what it sees.

Original description follows.

Drive a synthetic GT3 around a fictional circuit and stream the telemetry into
ATLAS Open Streaming.

    python produce.py                 # 2 laps
    python produce.py --laps 5
    python produce.py --seconds 30
    python produce.py --rate 100 --driver scruffy

No hardware, no simulator, no customer data, no licence. The point is that the
whole path - session, configuration, data formats, samples, markers - runs on
your machine with nothing but Docker.
"""

from __future__ import annotations

import argparse
import signal
import sys
import time

from atlas_lab.channels import CHANNELS
from atlas_lab.lapsim import GT3, REFERENCE_DRIVER, DriverModel, LapSimulator
from atlas_lab.writer import AtlasWriter

# ---------------------------------------------------------------------------
# MODULE 1. Replace this with your GitHub handle.
#
# It becomes part of the session identifier, so it travels with every packet
# and shows up in the recorded session. That is the point: a session is not an
# anonymous time window, it has an identity, and this is where it comes from.
LAB_HANDLE = "your-github-handle"  # keep this in step with produce.py
# ---------------------------------------------------------------------------

DRIVERS = {
    "reference": REFERENCE_DRIVER,
    # Brakes earlier, uses less of the car, gives away about three seconds.
    # Useful for step 5 when you want two laps that differ in an explainable way.
    "scruffy": DriverModel(commitment=0.93, brake_margin_m=18, trail_braking=0.25, seed=7),
}

_stop = False


def _handle_sigint(_sig, _frame):
    global _stop
    _stop = True
    print("\nStopping - the session will be closed cleanly.")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--laps", type=int, default=2, help="number of laps to stream (default 2)")
    p.add_argument("--seconds", type=float, default=None, help="stream for a fixed time instead")
    p.add_argument("--rate", type=int, default=60, help="sample rate in Hz (default 60)")
    p.add_argument("--driver", choices=sorted(DRIVERS), default="reference")
    p.add_argument("--batch-ms", type=int, default=100, help="samples per packet, in ms of data")
    p.add_argument("--session-name", default=None)
    p.add_argument("--realtime", action="store_true", default=True,
                   help="stream at wall-clock speed (default)")
    p.add_argument("--fast", dest="realtime", action="store_false",
                   help="stream as fast as possible - useful in CI")
    args = p.parse_args()

    signal.signal(signal.SIGINT, _handle_sigint)

    driver = DRIVERS[args.driver]
    sim = LapSimulator(car=GT3, driver=driver, rate_hz=args.rate)
    name = args.session_name or f"Sandbourne Park - {LAB_HANDLE} - {args.driver} - {time.strftime('%H:%M:%S')}"

    print(f"Circuit    : {sim.circuit.name} ({sum(s.length for s in sim.circuit.segments):.0f} m)")
    print(f"Car        : {GT3.name}")
    print(f"Driver     : {args.driver}")
    print(f"Ideal lap  : {sim.lap_time:.3f} s")
    print(f"Rate       : {args.rate} Hz")
    print()

    writer = AtlasWriter()
    print(f"Connecting to Stream API at {writer.stream_api_address} ...")
    writer.connect()
    print("Connected.")

    session_key = writer.start_session(name, CHANNELS)
    print(f"[1/3] Session   : {name}")
    # Machine-readable, for the lab validator. The session only gets this far
    # after a successful CreateSession round-trip to the Stream API, so
    # printing it is evidence the pipeline worked, not just a claim.
    print(f"LAB_SESSION={name}")
    print(f"[1/3] Key       : {session_key}")
    print(f"[2/3] Config    : {len(CHANNELS)} parameters, 1 group, both streams, essential")
    print(f"[3/3] Streaming : {'%d laps' % args.laps if args.seconds is None else '%.0f s' % args.seconds}")
    print()

    interval_ns = int(1e9 / args.rate)
    batch_size = max(1, int(args.rate * args.batch_ms / 1000))

    # Rule 5: timestamps must be contiguous. Track a running start time and
    # advance it by exactly the batch duration each time, rather than reading
    # the clock again - clock reads drift and leave gaps in the trace.
    timestamp_ns = time.time_ns()
    writer.write_marker(timestamp_ns, "Out Lap", "Lap Trigger", "Session start", 1)

    batch: dict[str, list[float]] = {c.key: [] for c in CHANNELS}
    samples_sent = 0
    laps_done = 0
    started = time.time()
    lap_started = timestamp_ns

    try:
        while not _stop:
            values, crossed_line = sim.step()
            for k, v in values.items():
                if k in batch:
                    batch[k].append(v)

            if crossed_line:
                laps_done += 1
                lap_end_ns = timestamp_ns + len(batch[CHANNELS[0].key]) * interval_ns
                writer.write_marker(
                    lap_end_ns, f"Lap {laps_done}", "Lap Trigger", "Start/finish crossing", laps_done + 1
                )
                print(f"  lap {laps_done} complete  ({(lap_end_ns - lap_started) / 1e9:.3f}s)")
                lap_started = lap_end_ns

            if len(batch[CHANNELS[0].key]) >= batch_size:
                n = len(batch[CHANNELS[0].key])
                writer.write_batch(batch, timestamp_ns, interval_ns)
                timestamp_ns = time.time_ns()
                samples_sent += n
                batch = {c.key: [] for c in CHANNELS}
                if args.realtime:
                    target = started + samples_sent / args.rate
                    delay = target - time.time()
                    if delay > 0:
                        time.sleep(delay)

            if args.seconds is not None:
                if samples_sent / args.rate >= args.seconds:
                    break
            elif laps_done >= args.laps:
                break

        # Flush whatever is left so the last fraction of a lap is not lost.
        remaining = len(batch[CHANNELS[0].key])
        if remaining:
            writer.write_batch(batch, timestamp_ns, interval_ns)
            timestamp_ns += remaining * interval_ns
            samples_sent += remaining

    finally:
        writer.end_session(timestamp_ns)
        writer.close()

    elapsed = time.time() - started
    print()
    print(f"Sent {samples_sent} samples x {len(CHANNELS)} channels "
          f"({samples_sent * len(CHANNELS)} values) in {elapsed:.1f}s.")
    print("Session ended cleanly.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
