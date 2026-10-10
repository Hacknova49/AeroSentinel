"""Same flow as run_demo.py but against the running Unity player (press Play first)."""
from aerosentinel.autonomy.unity_drone import UnityDrone
from aerosentinel_schemas import GeoPoint, SensorType

drone = UnityDrone()
print("state:", drone.get_state())
drone.fly_to(GeoPoint(lat=22.5045, lon=88.3045, alt_m=40))
for o in drone.capture([SensorType.WATER_LEVEL, SensorType.RGB], region_id="region-001", zone_id="region-001/z-11", patrol_id="manual"):
    print(o.sensor, o.readings, o.image_uri)
drone.dock()
drone.close()
