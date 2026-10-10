from datetime import datetime, timezone

import pytest
from aerosentinel_schemas import GeoPoint, Observation, SensorType
from aerosentinel_schemas.geo import haversine_m, offset
from pydantic import ValidationError


def test_naive_timestamp_rejected():
    with pytest.raises(ValidationError):
        Observation(region_id="r", zone_id="r/z1", patrol_id="p", sensor=SensorType.RGB,
                    timestamp=datetime(2026, 1, 1), position=GeoPoint(lat=0, lon=0))


def test_extra_fields_forbidden_and_frozen():
    obs = Observation(region_id="r", zone_id="r/z1", patrol_id="p", sensor=SensorType.RGB,
                      timestamp=datetime.now(timezone.utc), position=GeoPoint(lat=0, lon=0))
    with pytest.raises(ValidationError):
        obs.region_id = "other"
    with pytest.raises(ValidationError):
        Observation.model_validate({**obs.model_dump(), "surprise": 1})


def test_roundtrip_json():
    obs = Observation(region_id="r", zone_id="r/z1", patrol_id="p", sensor=SensorType.WATER_LEVEL,
                      timestamp=datetime.now(timezone.utc), position=GeoPoint(lat=22.5, lon=88.3),
                      readings={"water_level_m": 1.2})
    assert Observation.model_validate_json(obs.model_dump_json()) == obs


def test_offset_and_haversine_agree():
    a = GeoPoint(lat=22.5, lon=88.3)
    assert haversine_m(a, offset(a, north_m=300, east_m=400)) == pytest.approx(500, rel=1e-3)
