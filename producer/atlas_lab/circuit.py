"""
A fictional circuit.

Invented, not traced from a real venue. That is a licensing decision as much as
a technical one: the lab ships no real circuit geometry, and any track map it
draws is reconstructed from the telemetry itself.

A circuit is a closed sequence of segments. `curvature` is 1/radius in 1/m,
signed, positive = left. A straight has curvature 0.

Closing a layout needs two things to hold, and only the first is easy to design
by hand:

  1. the corner angles sum to a whole number of full turns, and
  2. the integrated position returns to the origin.

Because the heading profile depends only on the corners, once the corners are
fixed the second condition is *linear* in the straight lengths. `close_circuit`
solves it exactly with a minimum-norm correction, which spreads the adjustment
across every straight instead of distorting one.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Segment:
    length: float
    curvature: float
    name: str | None = None


@dataclass(frozen=True)
class Circuit:
    name: str
    segments: tuple[Segment, ...]


def corner(radius_m: float, angle_deg: float, name: str | None = None) -> Segment:
    angle = math.radians(abs(angle_deg))
    return Segment(
        length=radius_m * angle,
        curvature=math.copysign(1.0, angle_deg) / radius_m,
        name=name,
    )


def straight(length: float, name: str | None = None) -> Segment:
    return Segment(length=length, curvature=0.0, name=name)


def circuit_length(c: Circuit) -> float:
    return sum(s.length for s in c.segments)


def net_turn_degrees(c: Circuit) -> float:
    return math.degrees(sum(s.curvature * s.length for s in c.segments))


def _integrate(segments) -> tuple[float, float, float, list[float]]:
    """Walk the segments; return final x, y, heading, and per-segment headings."""
    x = y = h = 0.0
    headings: list[float] = []
    for seg in segments:
        headings.append(h)
        if seg.curvature == 0.0:
            x += math.cos(h) * seg.length
            y += math.sin(h) * seg.length
        else:
            r = 1.0 / seg.curvature
            dtheta = seg.curvature * seg.length
            dx = r * math.sin(dtheta)
            dy = r * (1.0 - math.cos(dtheta))
            x += dx * math.cos(h) - dy * math.sin(h)
            y += dx * math.sin(h) + dy * math.cos(h)
            h += dtheta
    return x, y, h, headings


def close_circuit(c: Circuit, tolerance_m: float = 0.01) -> Circuit:
    """Adjust straight lengths so the layout closes on itself exactly."""
    x, y, heading, headings = _integrate(c.segments)
    error = math.hypot(x, y)

    turns = math.degrees(heading) / 360.0
    if abs(turns - round(turns)) > 0.0015 or round(turns) == 0:
        raise ValueError(
            f'Circuit "{c.name}" turns {math.degrees(heading):.1f} degrees. '
            "A closed layout must turn a whole number of full turns."
        )
    if error <= tolerance_m:
        return c

    idx = [i for i, s in enumerate(c.segments) if s.curvature == 0.0]
    if len(idx) < 2:
        raise ValueError(f'Circuit "{c.name}" has too few straights to close.')

    cos_h = [math.cos(headings[i]) for i in idx]
    sin_h = [math.sin(headings[i]) for i in idx]

    # Minimum-norm solution of the 2 x k system A d = b.
    acc = sum(v * v for v in cos_h)
    acs = sum(cos_h[i] * sin_h[i] for i in range(len(idx)))
    ass = sum(v * v for v in sin_h)
    det = acc * ass - acs * acs
    if abs(det) < 1e-9:
        raise ValueError(f'Circuit "{c.name}" straights are parallel; cannot close by length.')

    l1 = (ass * -x - acs * -y) / det
    l2 = (-acs * -x + acc * -y) / det

    segments = list(c.segments)
    for k, i in enumerate(idx):
        delta = l1 * cos_h[k] + l2 * sin_h[k]
        new_length = segments[i].length + delta
        if new_length <= 5.0:
            raise ValueError(
                f'Closing "{c.name}" would shorten a straight to {new_length:.1f} m. '
                "Redesign the layout rather than forcing closure."
            )
        segments[i] = replace(segments[i], length=new_length)

    return Circuit(name=c.name, segments=tuple(segments))


# Sandbourne Park - a fictional clockwise circuit with a deliberately varied
# corner mix: a heavy stop, a fast sweeper, a technical infield and a long
# full-throttle straight. Varied on purpose so the telemetry has genuinely
# different corner types in it.
_SANDBOURNE_DESIGN = Circuit(
    name="Sandbourne Park",
    segments=(
        straight(1150, "Start/Finish straight"),
        corner(40, -95, "Ashcroft"),
        straight(200),
        corner(160, -55, "Kestrel"),
        straight(260),
        corner(65, 105, "The Loop"),
        straight(110),
        corner(28, -140, "Hairpin"),
        straight(520),
        corner(220, 40, "Sweeper"),
        straight(140),
        corner(50, -85, "Chapel"),
        straight(80),
        corner(46, 70, "Chapel exit"),
        straight(400),
        corner(95, -120, "Barn"),
        straight(180),
        corner(130, -80, "Onto the straight"),
    ),
)

SANDBOURNE = close_circuit(_SANDBOURNE_DESIGN)


def sample_centreline(c: Circuit, ds_m: float = 1.0):
    """
    Sample the centreline at a fixed spatial step.

    Corner entries and exits are smoothed over ~25 m. A real car does not step
    instantaneously from zero to full curvature, and an unsmoothed profile
    produces a steering trace with square edges that is obviously synthetic.
    """
    total = circuit_length(c)
    n = max(16, round(total / ds_m))
    ds = total / n

    edges: list[float] = []
    acc = 0.0
    for seg in c.segments:
        edges.append(acc)
        acc += seg.length

    raw_k = [0.0] * n
    segment_of = [0] * n
    for i in range(n):
        s = i * ds
        idx = 0
        for j in range(len(c.segments) - 1, -1, -1):
            if s >= edges[j]:
                idx = j
                break
        raw_k[i] = c.segments[idx].curvature
        segment_of[i] = idx

    win = max(3, int(round(25 / ds)) | 1)
    half = (win - 1) // 2
    curvature = [
        sum(raw_k[(i + d) % n] for d in range(-half, half + 1)) / win for i in range(n)
    ]

    heading = [0.0] * n
    xs = [0.0] * n
    ys = [0.0] * n
    ss = [0.0] * n
    h = px = py = 0.0
    for i in range(n):
        heading[i] = h
        xs[i] = px
        ys[i] = py
        ss[i] = i * ds
        px += math.cos(h) * ds
        py += math.sin(h) * ds
        h += curvature[i] * ds

    return {
        "curvature": curvature,
        "heading": heading,
        "x": xs,
        "y": ys,
        "s": ss,
        "segment_of": segment_of,
        "ds": ds,
        "n": n,
    }
