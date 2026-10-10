"""Conventions shared by every contract: WGS84, UTC, consistent IDs."""
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Annotated
from uuid import uuid4

from pydantic import AfterValidator, BaseModel, ConfigDict, Field

SCHEMA_VERSION = "0.1.0"

RegionId = str   # e.g. "region-001"
ZoneId = str     # e.g. "region-001/z-03"  (always prefixed by its region)


def _ensure_utc(v: datetime) -> datetime:
    if v.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware; use UTC")
    return v.astimezone(timezone.utc)


UtcDatetime = Annotated[datetime, AfterValidator(_ensure_utc)]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12]}"


class Contract(BaseModel):
    """Base for all contracts: immutable, no unknown fields."""
    model_config = ConfigDict(frozen=True, extra="forbid")


class GeoPoint(Contract):
    """WGS84 position. alt_m is metres above ground level (AGL) unless stated."""
    lat: float = Field(ge=-90, le=90)
    lon: float = Field(ge=-180, le=180)
    alt_m: float = 0.0


class BoundingBox(Contract):
    south: float = Field(ge=-90, le=90)
    west: float = Field(ge=-180, le=180)
    north: float = Field(ge=-90, le=90)
    east: float = Field(ge=-180, le=180)


class HazardType(StrEnum):
    FLOOD = "flood"
    FIRE = "fire"
    SMOKE = "smoke"
    LANDSLIDE = "landslide"
    STRUCTURAL_CRACK = "structural_crack"


class SensorType(StrEnum):
    RGB = "rgb"
    THERMAL = "thermal"
    WATER_LEVEL = "water_level"
    RAINFALL = "rainfall"
    SOIL_MOISTURE = "soil_moisture"
    WEATHER = "weather"


class Severity(StrEnum):
    INFO = "info"
    WATCH = "watch"
    WARNING = "warning"
    CRITICAL = "critical"
