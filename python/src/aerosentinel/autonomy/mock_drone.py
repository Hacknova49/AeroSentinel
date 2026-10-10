"""C1: MockDrone - kinematic drone with a battery model, driven by any `World`."""
from __future__ import annotations

from collections.abc import Sequence
from datetime import timedelta

from aerosentinel_schemas import (
    DroneError,
    DroneInterface,
    DroneMode,
    DroneState,
    GeoPoint,
    Observation,
    SensorType,
)
from aerosentinel_schemas.geo import haversine_m

from aerosentinel.autonomy.clock import Clock
from aerosentinel.geosim.world import World


class MockDrone(DroneInterface):
    def __init__(self, world: World, clock: Clock, dock_position: GeoPoint, *,
                 battery_pct: float = 100.0, drain_pct_per_km: float = 4.0) -> None:
        self.world, self.clock, self.dock_position = world, clock, dock_position
        self.drain_pct_per_km = drain_pct_per_km
        self._pos, self._battery, self._mode = dock_position, battery_pct, DroneMode.DOCKED

    def _move(self, target: GeoPoint, speed_mps: float) -> None:
        dist = haversine_m(self._pos, target)
        cost = dist / 1000 * self.drain_pct_per_km
        if cost > self._battery:
            self._mode = DroneMode.ERROR
            raise DroneError("battery depleted in flight")
        self.clock.advance(timedelta(seconds=dist / max(speed_mps, 0.1)))
        self._battery -= cost
        self._pos = target

    def fly_to(self, point: GeoPoint, speed_mps: float = 10.0) -> None:
        self._mode = DroneMode.FLYING
        self._move(point, speed_mps)

    def get_state(self) -> DroneState:
        return DroneState(position=self._pos, battery_pct=self._battery, mode=self._mode, timestamp=self.clock.now())

    def capture(self, sensors: Sequence[SensorType], *, region_id: str, zone_id: str, patrol_id: str) -> list[Observation]:
        t = self.clock.now()
        samples = self.world.sample(self._pos, t, list(sensors))
        return [Observation(region_id=region_id, zone_id=zone_id, patrol_id=patrol_id, sensor=s,
                            timestamp=t, position=self._pos, readings=samples.get(s, {})) for s in sensors]

    def dock(self) -> None:
        self._move(self.dock_position, 10.0)
        self._mode = DroneMode.DOCKED

    def battery_level(self) -> float:
        return self._battery

    # --- used by DockSimulator only (not part of DroneInterface) ---
    def _charge(self, pct: float) -> None:
        self._battery = min(100.0, self._battery + pct)
