"""One simulated patrol in the 2D geo-sim, printing the resulting alert."""
from datetime import datetime, timedelta, timezone

from aerosentinel.autonomy.clock import SimClock
from aerosentinel.autonomy.dock import DockSimulator
from aerosentinel.autonomy.mock_drone import MockDrone
from aerosentinel.autonomy.scheduler import MissionScheduler
from aerosentinel.geosim.world import FloodWorld, GridZones
from aerosentinel.intelligence.alerts import AlertEngine
from aerosentinel.perception.detection import ThresholdDetector
from aerosentinel.perception.measurement import measure
from aerosentinel.storage.repository import InMemoryRepository
from aerosentinel_schemas import BoundingBox, GeoPoint

t0 = datetime(2026, 7, 1, tzinfo=timezone.utc)
dock = GeoPoint(lat=22.5, lon=88.3)
zones = GridZones("region-001", BoundingBox(south=22.5, west=88.3, north=22.509, east=88.309))
world = FloodWorld(zones, GeoPoint(lat=22.5045, lon=88.3045), start=t0 - timedelta(hours=2))
clock, repo = SimClock(t0), InMemoryRepository()
drone = MockDrone(world, clock, dock)
res = MissionScheduler(drone, clock, DockSimulator(), zones, dock, sink=repo.add_observations).run_patrol()
engine, det = AlertEngine(repo), ThresholdDetector()
for o in res.observations:
    for d in det.detect(o):
        engine.on_detection(d, o.region_id, o.zone_id, measurement=measure(d, o))
print(f"patrol {res.patrol_id}: {len(res.route.waypoints)} waypoints, {len(res.observations)} observations, "
      f"{(res.finished - res.started).total_seconds()/60:.0f} min sim time")
for a in repo.alerts("region-001"):
    print(f"ALERT [{a.severity.value}] {a.zone_id} - {a.message}")
