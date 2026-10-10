"""The frozen contracts (section 1.2 of the module breakdown).

Observation, Detection, Measurement, AnomalyEvent, VerifiedAnomaly, RiskScore,
Alert, Route, MissionRequest (+ DroneState). DroneInterface lives in drone_interface.py.
"""
from __future__ import annotations

from enum import StrEnum

from pydantic import Field

from .common import (
    BoundingBox,
    Contract,
    GeoPoint,
    HazardType,
    RegionId,
    SensorType,
    Severity,
    UtcDatetime,
    ZoneId,
    new_id,
    utcnow,
)


class Observation(Contract):
    """One capture from one sensor at one place and time."""
    id: str = Field(default_factory=lambda: new_id("obs"))
    region_id: RegionId
    zone_id: ZoneId
    patrol_id: str
    sensor: SensorType
    timestamp: UtcDatetime
    position: GeoPoint
    image_uri: str | None = None                       # RGB / thermal frames
    readings: dict[str, float] = Field(default_factory=dict)  # scalar sensors


class Detection(Contract):
    """A hazard found in an Observation (D1)."""
    id: str = Field(default_factory=lambda: new_id("det"))
    observation_id: str
    hazard: HazardType
    confidence: float = Field(ge=0, le=1)
    bbox_xywh: tuple[float, float, float, float] | None = None   # normalised 0..1
    geo: GeoPoint | None = None
    model_version: str


class Measurement(Contract):
    """Quantified severity of a Detection (D2)."""
    id: str = Field(default_factory=lambda: new_id("mea"))
    detection_id: str
    metric: str            # e.g. "water_depth", "burn_area"
    value: float
    unit: str              # SI, e.g. "m", "m2"
    uncertainty: float | None = None


class AnomalyEvent(Contract):
    """An unusual / accelerating change flagged on a time series (D3)."""
    id: str = Field(default_factory=lambda: new_id("anom"))
    region_id: RegionId
    zone_id: ZoneId
    metric: str
    method: str            # "zscore" | "cusum" | "isolation_forest" ...
    score: float
    timestamp: UtcDatetime
    note: str = ""


class VerifiedAnomaly(Contract):
    """Result of the Investigate state (C5): did the drone confirm the issue?"""
    id: str = Field(default_factory=lambda: new_id("vano"))
    anomaly_id: str
    verified: bool
    hazard: HazardType | None = None
    confidence: float = Field(ge=0, le=1)
    evidence_observation_ids: list[str] = Field(default_factory=list)
    timestamp: UtcDatetime = Field(default_factory=utcnow)


class RiskScore(Contract):
    """Forecast risk for a zone (D4)."""
    region_id: RegionId
    zone_id: ZoneId
    hazard: HazardType
    score: float = Field(ge=0, le=1)
    horizon_hours: int = Field(gt=0)
    model_version: str
    timestamp: UtcDatetime
    drivers: dict[str, float] = Field(default_factory=dict)   # explainability


class AlertStatus(StrEnum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"


class Alert(Contract):
    id: str = Field(default_factory=lambda: new_id("alert"))
    dedupe_key: str                       # "<zone_id>:<hazard>"
    region_id: RegionId
    zone_id: ZoneId
    hazard: HazardType
    severity: Severity
    verified: bool = False
    risk_score: float | None = Field(default=None, ge=0, le=1)
    message: str = ""
    status: AlertStatus = AlertStatus.OPEN
    created_at: UtcDatetime
    updated_at: UtcDatetime


class Route(Contract):
    id: str = Field(default_factory=lambda: new_id("route"))
    region_id: RegionId
    waypoints: list[GeoPoint] = Field(min_length=1)
    est_duration_s: float = Field(ge=0)
    est_battery_pct: float = Field(ge=0)


class MissionKind(StrEnum):
    PATROL = "patrol"
    INVESTIGATE = "investigate"


class MissionRequest(Contract):
    id: str = Field(default_factory=lambda: new_id("mission"))
    kind: MissionKind
    region_id: RegionId
    area: BoundingBox | None = None       # PATROL
    target: GeoPoint | None = None        # INVESTIGATE
    priority: int = Field(default=0, ge=0, le=10)
    requested_at: UtcDatetime = Field(default_factory=utcnow)


class DroneMode(StrEnum):
    DOCKED = "docked"
    FLYING = "flying"
    ERROR = "error"


class DroneState(Contract):
    position: GeoPoint
    battery_pct: float = Field(ge=0, le=100)
    mode: DroneMode
    timestamp: UtcDatetime
