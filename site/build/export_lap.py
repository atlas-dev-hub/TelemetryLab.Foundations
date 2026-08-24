#!/usr/bin/env python3
"""
Export one real lap for the site's hero.

The landing page animates actual telemetry from the lab's own simulator — the
same code a learner runs in Module 1 — rather than a decorative squiggle. It
costs nothing to be truthful here, and the alternative is a site about telemetry
that shows made-up telemetry.

Downsampled to keep the payload small; the shape and the speed profile survive
intact.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "producer"))

from atlas_lab.circuit import SANDBOURNE, circuit_length, sample_centreline  # noqa: E402
from atlas_lab.lapsim import GT3, REFERENCE_DRIVER, LapSimulator  # noqa: E402

TARGET_POINTS = 520
OUT = os.path.join(HERE, "..", "public", "lap.json")


def main() -> int:
    sim = LapSimulator(circuit=SANDBOURNE, car=GT3, driver=REFERENCE_DRIVER, rate_hz=60)
    geo = sample_centreline(SANDBOURNE, 1.0)
    n = geo["n"]

    step = max(1, n // TARGET_POINTS)
    idx = list(range(0, n, step))

    speeds = [sim._speed[i] for i in idx]
    v_min, v_max = min(speeds), max(speeds)

    xs = [geo["x"][i] for i in idx]
    ys = [geo["y"][i] for i in idx]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    lap = {
        "circuit": SANDBOURNE.name,
        "car": GT3.name,
        "lengthM": round(circuit_length(SANDBOURNE)),
        "lapTime": round(sim.lap_time, 3),
        "bounds": [round(min_x, 1), round(min_y, 1), round(max_x, 1), round(max_y, 1)],
        "speedRange": [round(v_min, 2), round(v_max, 2)],
        # x, y in metres; v normalised 0..1 for the colour ramp; kph for labels.
        "points": [
            {
                "x": round(geo["x"][i], 1),
                "y": round(geo["y"][i], 1),
                "v": round((sim._speed[i] - v_min) / (v_max - v_min), 4),
                "kph": round(sim._speed[i] * 3.6),
            }
            for i in idx
        ],
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(lap, f, separators=(",", ":"))

    size = os.path.getsize(OUT) / 1024
    print(f"{len(lap['points'])} points, {size:.1f} kB")
    print(f"{lap['circuit']} — {lap['lengthM']} m — {lap['lapTime']}s — "
          f"{round(v_min * 3.6)}–{round(v_max * 3.6)} km/h")
    return 0


if __name__ == "__main__":
    sys.exit(main())
