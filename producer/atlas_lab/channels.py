"""
The channel registry.

Each entry maps a simulator key to an ATLAS parameter definition. This is the
part a generic time-series stack has no equivalent of: a channel is not just a
name and a number, it has an identity, units, a sample rate, a valid range and
a display format, and every consumer downstream gets those for free.

Step 4 of the walkthrough asks you to add one. Everything needed to do that is
in this file.
"""

from __future__ import annotations

from dataclasses import dataclass

APPLICATION = "SandbourneGT3"
GROUP = "Car"


@dataclass(frozen=True)
class ChannelDef:
    key: str            # simulator key
    units: str
    description: str
    format_string: str
    min_value: float
    max_value: float
    frequency: int = 60

    @property
    def identifier(self) -> str:
        # ATLAS parameter identifiers are "<name>:<application>".
        return f"{self.key}:{APPLICATION}"


CHANNELS: tuple[ChannelDef, ...] = (
    ChannelDef("Speed", "m/s", "Ground speed", "%6.2f", 0, 100),
    ChannelDef("Throttle", "%", "Throttle pedal position", "%6.1f", 0, 100),
    ChannelDef("Brake", "%", "Brake pedal position", "%6.1f", 0, 100),
    ChannelDef("Gear", "", "Selected gear", "%3.0f", 0, 8),
    ChannelDef("RPM", "rpm", "Engine speed", "%7.0f", 0, 9000),
    ChannelDef("SteeringAngle", "deg", "Steering wheel angle", "%7.2f", -360, 360),
    ChannelDef("LatAccel", "g", "Lateral acceleration", "%6.3f", -3, 3),
    ChannelDef("LongAccel", "g", "Longitudinal acceleration", "%6.3f", -3, 3),
    ChannelDef("Yaw", "deg", "Heading in the world frame", "%7.2f", -360, 360),
    ChannelDef("LapDistance", "m", "Distance travelled this lap", "%8.1f", 0, 10000),
    ChannelDef("LapNumber", "", "Lap counter", "%4.0f", 0, 9999),
)

BY_KEY = {c.key: c for c in CHANNELS}
