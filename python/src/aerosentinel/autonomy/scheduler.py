"""C3: Deploy -> Patrol -> Return -> Recharge -> Redeploy loop with interval timing."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime, timedelta

from aerosentinel_schemas import DroneInterface, GeoPoint, Observation, Route, SensorType, new_id

from aerosentinel.autonomy.clock import Clock
from aerosentinel.autonomy.dock import DockSimulator
from aerosentinel.autonomy.mock_drone import MockDrone
from aerosentinel.autonomy.planner import fits_battery, plan_patrol
from aerosentinel.geosim.world import GridZones

DEFAULT_SENSORS = (SensorType.WATER_LEVEL, SensorType.RAINFALL, SensorType.SOIL_MOISTURE)


@dataclass
class PatrolResult:
    patrol_id: str
    route: Route
    observations: list[Observation]
    started: datetime
    finished: datetime


class MissionScheduler:
    def __init__(self, drone: DroneInterface, clock: Clock, dock_sim: DockSimulator, zones: GridZones,
                 dock_position: GeoPoint, *, interval: timedelta = timedelta(hours=6),
                 sensors: Sequence[SensorType] = DEFAULT_SENSORS,
                 sink: Callable[[list[Observation]], None] = lambda obs: None) -> None:
        self.drone, self.clock, self.dock_sim, self.zones = drone, clock, dock_sim, zones
        self.dock_position, self.interval, self.sensors, self.sink = dock_position, interval, sensors, sink
        self._next_start = clock.now()

    def run_patrol(self) -> PatrolResult:
        self.clock.sleep_until(self._next_start)
        started, patrol_id = self.clock.now(), new_id("patrol")
        self._next_start = started + self.interval
        route = plan_patrol(self.zones.region_id, self.zones.area, self.dock_position)
        if not fits_battery(route, self.drone.battery_level()):
            raise RuntimeError("battery too low for planned route; recharge first")
        collected: list[Observation] = []
        for wp in route.waypoints:                                   # Deploy + Patrol
            self.drone.fly_to(wp)
            obs = self.drone.capture(self.sensors, region_id=self.zones.region_id,
                                     zone_id=self.zones.zone_of(wp), patrol_id=patrol_id)
            collected += obs
            self.sink(obs)
        self.drone.dock()                                            # Return
        if isinstance(self.drone, MockDrone):                        # Recharge (sim only)
            self.dock_sim.recharge(self.drone)
        return PatrolResult(patrol_id, route, collected, started, self.clock.now())
