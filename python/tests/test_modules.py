from datetime import datetime, timezone

from aerosentinel.autonomy.planner import fits_battery, plan_patrol
from aerosentinel.datagen.generator import generate_history
from aerosentinel.intelligence.alerts import AlertEngine
from aerosentinel.intelligence.risk import BaselineRiskModel
from aerosentinel.intelligence.trend import cusum_change, zscore_latest
from aerosentinel.storage.repository import InMemoryRepository
from aerosentinel_schemas import BoundingBox, GeoPoint, Severity

T0 = datetime(2026, 7, 1, tzinfo=timezone.utc)
DOCK = GeoPoint(lat=22.5, lon=88.3)


def test_planner_covers_area_and_fits_battery():
    r = plan_patrol("r", BoundingBox(south=22.5, west=88.3, north=22.509, east=88.309), DOCK)
    assert len(r.waypoints) >= 4 and fits_battery(r, 100)


def test_trend_detectors():
    flat = [1.0, 1.1, 0.9] * 10
    assert abs(zscore_latest(flat + [1.0])) < 3 and zscore_latest(flat + [9.0]) > 3
    assert cusum_change(flat + [3.0 + i for i in range(10)])


def test_alert_escalates_not_downgrades():
    eng = AlertEngine(InMemoryRepository())
    hi = BaselineRiskModel().predict("r", "r/z1", T0, soil_moisture=0.95, rain_mm_h=20, level_slope_m_per_day=0.5)
    lo = BaselineRiskModel().predict("r", "r/z1", T0, soil_moisture=0.65, rain_mm_h=8, level_slope_m_per_day=0.05)
    a1 = eng.on_risk(hi)
    a2 = eng.on_risk(lo)
    assert a1 and a1.severity == Severity.WARNING
    assert a2 is None or a2.severity == Severity.WARNING


def test_datagen_uses_production_schema():
    obs, truth = generate_history("r", ["r/z1", "r/z2"], DOCK, days=30)
    assert len(obs) == 2 * 30 * 3 and len(truth) == 60
