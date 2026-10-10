"""B2: synthetic long-horizon history in the PRODUCTION schema (months in seconds).

Each day per zone: rainfall, soil moisture, water level, with a seasonal cycle and
injected flood windows preceded by a soil-saturation drift (so D4 has something to learn).
Returns Observations + ground-truth labels for supervised training/evaluation.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from aerosentinel_schemas import GeoPoint, Observation, SensorType


@dataclass
class GroundTruth:
    zone_id: str
    day: int
    flood: bool


def generate_history(
    region_id: str, zones: list[str], origin: GeoPoint, days: int = 180,
    start: datetime = datetime(2026, 1, 1, tzinfo=timezone.utc), seed: int = 0,
) -> tuple[list[Observation], list[GroundTruth]]:
    rng, obs, truth = random.Random(seed), [], []
    for zone in zones:
        soil, level, event_left = 0.4, 0.2, 0
        for d in range(days):
            season = 0.5 + 0.5 * math.sin(2 * math.pi * (d - 60) / 365)       # monsoon-like
            rain = max(0.0, rng.gauss(10 * season, 4))
            soil = min(1.0, max(0.0, 0.9 * soil + 0.02 * rain + rng.gauss(0, 0.01)))
            level = max(0.0, 0.85 * level + 0.01 * rain + 0.5 * max(0, soil - 0.7) + rng.gauss(0, 0.01))
            if event_left == 0 and soil > 0.8 and rng.random() < 0.15:
                event_left = rng.randint(2, 5)
            flood = event_left > 0
            if flood:
                level += 1.0
                event_left -= 1
            ts = start + timedelta(days=d, hours=6)
            for sensor, readings in (
                (SensorType.RAINFALL, {"rain_mm_h": rain}),
                (SensorType.SOIL_MOISTURE, {"soil_moisture": soil}),
                (SensorType.WATER_LEVEL, {"water_level_m": level}),
            ):
                obs.append(Observation(region_id=region_id, zone_id=zone, patrol_id=f"synthetic-{d}",
                                       sensor=sensor, timestamp=ts, position=origin, readings=readings))
            truth.append(GroundTruth(zone, d, flood))
    return obs, truth
