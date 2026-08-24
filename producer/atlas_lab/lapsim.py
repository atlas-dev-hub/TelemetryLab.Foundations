"""
Synthetic lap generation.

A quasi-steady-state lap simulation: find the cornering-limited speed at every
point on the circuit, then constrain it by how hard the car can brake into each
corner and accelerate out. This is the standard lap-time-simulation approach,
and using it rather than drawing plausible-looking curves matters - the traces
have to survive an engineer looking at them, and derived quantities (lateral
load, trail braking, throttle application) have to be physically consistent
with each other and with the speed trace.

Nothing here is derived from any confidential or customer data. It is a car
model, a fictional circuit, and Newton's second law.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .circuit import SANDBOURNE, Circuit, sample_centreline


@dataclass(frozen=True)
class CarModel:
    name: str
    lat_accel_max: float  # m/s^2
    decel_max: float  # m/s^2
    accel_max: float  # m/s^2
    v_max: float  # m/s
    shift_speeds: tuple[float, ...]  # m/s, ascending
    redline_rpm: float
    wheelbase_m: float
    steering_ratio: float


GT3 = CarModel(
    name="GT3",
    lat_accel_max=19.0,  # ~1.9 g with aero
    decel_max=22.0,  # ~2.2 g
    accel_max=8.5,
    v_max=79.0,  # ~284 km/h
    shift_speeds=(17, 27, 38, 50, 63),
    redline_rpm=8500,
    wheelbase_m=2.6,
    steering_ratio=13,
)


@dataclass(frozen=True)
class DriverModel:
    commitment: float = 0.99  # fraction of the car's limit actually used
    brake_margin_m: float = 2.0  # extra braking margin before each corner
    trail_braking: float = 0.55  # how much pressure is carried into the corner
    seed: int = 1


REFERENCE_DRIVER = DriverModel()


def _mulberry32(seed: int):
    """Deterministic PRNG - reproducible telemetry beats entropy for a lab."""
    a = seed & 0xFFFFFFFF

    def rand() -> float:
        nonlocal a
        a = (a + 0x6D2B79F5) & 0xFFFFFFFF
        t = a
        t = (t ^ (t >> 15)) * (1 | t) & 0xFFFFFFFF
        t = (t + ((t ^ (t >> 7)) * (61 | t) & 0xFFFFFFFF)) ^ t
        t &= 0xFFFFFFFF
        return ((t ^ (t >> 14)) & 0xFFFFFFFF) / 4294967296.0

    return rand


def _smooth_noise(n: int, scale: float, rand) -> list[float]:
    """Band-limited noise: reads as a human, not as dither."""
    coarse = [(rand() * 2 - 1) * scale for _ in range(max(2, math.ceil(n / 30)) + 1)]
    out = [0.0] * n
    for i in range(n):
        p = (i / n) * (len(coarse) - 1)
        i0 = int(p)
        f = p - i0
        a = coarse[i0]
        b = coarse[min(i0 + 1, len(coarse) - 1)]
        out[i] = a + (b - a) * (f * f * (3 - 2 * f))
    return out


def _clamp01(x: float) -> float:
    return 0.0 if x < 0 else 1.0 if x > 1 else x


class LapSimulator:
    """
    Produces a continuous stream of samples around a circuit, lap after lap.

    Held as state rather than returned as an array so the producer can stream
    indefinitely at a fixed rate, the way a real data source does, and so lap
    boundaries fall out naturally as markers.
    """

    def __init__(
        self,
        circuit: Circuit = SANDBOURNE,
        car: CarModel = GT3,
        driver: DriverModel = REFERENCE_DRIVER,
        rate_hz: int = 60,
    ) -> None:
        self.circuit = circuit
        self.car = car
        self.driver = driver
        self.rate_hz = rate_hz

        geo = sample_centreline(circuit, 1.0)
        self._geo = geo
        self._n = geo["n"]
        self._ds = geo["ds"]
        self._speed = self._solve_speed_profile()
        self._time_at = self._integrate_time()
        self.lap_time = self._time_at[-1]

        rand = _mulberry32(driver.seed)
        m = max(2, round(self.lap_time * rate_hz))
        self._throttle_noise = _smooth_noise(m, 0.02, rand)
        self._brake_noise = _smooth_noise(m, 0.015, rand)
        self._steer_noise = _smooth_noise(m, 0.012, rand)
        self._noise_len = m

        self._t_in_lap = 0.0
        self.lap_number = 1
        self._prev_brake = 0.0
        self._trail_left = 0

    def _solve_speed_profile(self) -> list[float]:
        car, driver = self.car, self.driver
        n, ds = self._n, self._ds
        k = self._geo["curvature"]

        lat_max = car.lat_accel_max * driver.commitment
        decel_max = car.decel_max * driver.commitment
        accel_max = car.accel_max * driver.commitment

        # 1. Cornering-limited speed everywhere.
        v = [
            car.v_max if abs(k[i]) < 1e-6 else min(car.v_max, math.sqrt(lat_max / abs(k[i])))
            for i in range(n)
        ]

        # 2. Braking and acceleration limits, applied around the closed loop.
        for _ in range(3):
            for c in range(n):  # backward: can only arrive if already slow enough
                i = n - 1 - c
                j = (i + 1) % n
                limit = math.sqrt(v[j] * v[j] + 2 * decel_max * ds)
                if limit < v[i]:
                    v[i] = limit
            for i in range(n):  # forward: can only reach v[i] given finite grip
                p = (i - 1) % n
                limit = math.sqrt(v[p] * v[p] + 2 * accel_max * ds)
                if limit < v[i]:
                    v[i] = limit

        # 3. Driver margin: lift a little earlier than the theoretical limit.
        shift = int(round(driver.brake_margin_m / ds))
        if shift > 0:
            v = [min(v[i], v[(i + shift) % n]) for i in range(n)]
        return v

    def _integrate_time(self) -> list[float]:
        n, ds, v = self._n, self._ds, self._speed
        t = [0.0] * (n + 1)
        for i in range(n):
            v_avg = max(1.0, (v[i] + v[(i + 1) % n]) / 2.0)
            t[i + 1] = t[i] + ds / v_avg
        return t

    def _station_at(self, t_in_lap: float) -> tuple[int, float]:
        """Binary search the time table for the station index and fraction."""
        lo, hi = 0, self._n
        while lo < hi:
            mid = (lo + hi) // 2
            if self._time_at[mid] <= t_in_lap:
                lo = mid + 1
            else:
                hi = mid
        i = max(0, lo - 1)
        t0, t1 = self._time_at[i], self._time_at[i + 1]
        f = 0.0 if t1 <= t0 else min(1.0, max(0.0, (t_in_lap - t0) / (t1 - t0)))
        return i, f

    def step(self) -> tuple[dict[str, float], bool]:
        """
        Advance one sample.

        Returns the channel values and whether this sample crossed the
        start/finish line, which the producer turns into a lap marker.
        """
        dt = 1.0 / self.rate_hz
        crossed = False

        self._t_in_lap += dt
        if self._t_in_lap >= self.lap_time:
            self._t_in_lap -= self.lap_time
            self.lap_number += 1
            crossed = True

        geo = self._geo
        n = self._n
        i, f = self._station_at(self._t_in_lap)
        j = (i + 1) % n

        speed = self._speed[i] + (self._speed[j] - self._speed[i]) * f
        curv = geo["curvature"][i] + (geo["curvature"][j] - geo["curvature"][i]) * f
        lap_dist = geo["s"][i] + self._ds * f

        # Longitudinal acceleration from the speed profile, one step ahead.
        i2, f2 = self._station_at(min(self._t_in_lap + dt, self.lap_time - 1e-6))
        j2 = (i2 + 1) % n
        speed_next = self._speed[i2] + (self._speed[j2] - self._speed[i2]) * f2
        long_accel = (speed_next - speed) / dt

        lat_accel = speed * speed * curv
        lat_max = self.car.lat_accel_max * self.driver.commitment
        accel_max = self.car.accel_max * self.driver.commitment
        decel_max = self.car.decel_max * self.driver.commitment

        ni = int(self._t_in_lap * self.rate_hz) % self._noise_len

        if long_accel >= 0:
            throttle = _clamp01(long_accel / accel_max + 0.05 + self._throttle_noise[ni])
            brake = 0.0
        else:
            brake = _clamp01(-long_accel / decel_max + self._brake_noise[ni])
            lateral_use = min(1.0, abs(lat_accel) / lat_max)
            throttle = _clamp01((1 - lateral_use) * 0.06)

        # Cornering hard at steady speed means partial throttle, not coasting.
        if abs(long_accel) < 0.6 and abs(lat_accel) > lat_max * 0.4:
            throttle = _clamp01(
                0.35 + 0.4 * (1 - abs(lat_accel) / lat_max) + self._throttle_noise[ni]
            )

        # Trail braking: pressure bleeds off into the corner rather than
        # releasing the instant the car stops decelerating.
        if brake == 0.0 and self._prev_brake > 0.05 and self._trail_left == 0:
            self._trail_left = int(self.rate_hz * 0.45 * self.driver.trail_braking)
            self._trail_from = self._prev_brake * self.driver.trail_braking
            self._trail_total = max(1, self._trail_left)
        if self._trail_left > 0:
            decay = self._trail_from * (self._trail_left / self._trail_total)
            brake = max(brake, decay)
            self._trail_left -= 1
        self._prev_brake = brake

        gear = 1
        for s_i, s_v in enumerate(self.car.shift_speeds):
            if speed > s_v:
                gear = s_i + 2
        lo = 0.0 if gear == 1 else self.car.shift_speeds[gear - 2]
        hi = (
            self.car.shift_speeds[gear - 1]
            if gear - 1 < len(self.car.shift_speeds)
            else self.car.v_max
        )
        frac = (speed - lo) / (hi - lo) if hi > lo else 0.0
        rpm = 3200 + _clamp01(frac) * (self.car.redline_rpm - 3200)

        road_wheel = math.atan(self.car.wheelbase_m * curv)
        steering = math.degrees(road_wheel * self.car.steering_ratio) + self._steer_noise[ni] * 3

        return (
            {
                "Speed": speed,
                "Throttle": throttle * 100.0,
                "Brake": brake * 100.0,
                "Gear": float(gear),
                "RPM": rpm,
                "SteeringAngle": steering,
                "LatAccel": lat_accel / 9.80665,
                "LongAccel": long_accel / 9.80665,
                "Yaw": math.degrees(geo["heading"][i]),
                "LapDistance": lap_dist,
                "LapNumber": float(self.lap_number),
            },
            crossed,
        )
