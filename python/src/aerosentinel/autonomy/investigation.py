"""C5: Patrol <-> Investigate state machine: approach, orbit, re-capture, verify."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from enum import StrEnum

from aerosentinel_schemas import (
    DroneInterface,
    GeoPoint,
    HazardType,
    Observation,
    SensorType,
    VerifiedAnomaly,
    new_id,
)
from aerosentinel_schemas.geo import offset

# verifier(observations) -> (verified, confidence, hazard)
Verifier = Callable[[list[Observation]], tuple[bool, float, HazardType | None]]


class State(StrEnum):
    PATROL = "patrol"
    APPROACH = "approach"
    ORBIT = "orbit"
    VERIFY = "verify"


class InvestigationController:
    def __init__(self, drone: DroneInterface, verifier: Verifier, *, orbit_radius_m: float = 30.0,
                 alt_m: float = 25.0, sensors: Sequence[SensorType] = (SensorType.WATER_LEVEL, SensorType.RGB)) -> None:
        self.drone, self.verifier, self.r, self.alt, self.sensors = drone, verifier, orbit_radius_m, alt_m, sensors
        self.state = State.PATROL

    def investigate(self, anomaly_id: str, target: GeoPoint, region_id: str, zone_id: str) -> VerifiedAnomaly:
        pid, evidence = new_id("inv"), []
        self.state = State.APPROACH
        self.drone.fly_to(offset(target, alt_m=self.alt))
        self.state = State.ORBIT
        for n, e in ((self.r, 0), (0, self.r), (-self.r, 0), (0, -self.r)):
            self.drone.fly_to(offset(target, north_m=n, east_m=e, alt_m=self.alt), speed_mps=5.0)
            evidence += self.drone.capture(self.sensors, region_id=region_id, zone_id=zone_id, patrol_id=pid)
        self.state = State.VERIFY
        verified, conf, hazard = self.verifier(evidence)
        self.state = State.PATROL
        return VerifiedAnomaly(anomaly_id=anomaly_id, verified=verified, hazard=hazard, confidence=conf,
                               evidence_observation_ids=[o.id for o in evidence])
