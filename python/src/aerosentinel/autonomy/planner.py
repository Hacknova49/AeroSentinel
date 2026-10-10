"""C4: coverage (lawn-mower) path planning within battery limits."""
from __future__ import annotations

import math

from aerosentinel_schemas import BoundingBox, GeoPoint, Route
from aerosentinel_schemas.geo import haversine_m, offset


def plan_patrol(region_id: str, area: BoundingBox, dock: GeoPoint, *, altitude_m: float = 40.0,
                swath_m: float = 60.0, sample_spacing_m: float = 100.0, speed_mps: float = 10.0, drain_pct_per_km: float = 4.0) -> Route:
    sw = GeoPoint(lat=area.south, lon=area.west)
    width = haversine_m(sw, GeoPoint(lat=area.south, lon=area.east))
    height = haversine_m(sw, GeoPoint(lat=area.north, lon=area.west))
    rows = max(1, math.ceil(height / swath_m))
    wps: list[GeoPoint] = []
    for i in range(rows):
        y = min(height, swath_m / 2 + i * swath_m)
        n = max(1, math.ceil(width / sample_spacing_m))          # sample points along each sweep row
        xs = [width * k / n for k in range(n + 1)]
        xs = xs if i % 2 == 0 else xs[::-1]
        wps += [offset(sw, north_m=y, east_m=x, alt_m=altitude_m) for x in xs]
    path = [dock, *wps, dock]
    length = sum(haversine_m(a, b) for a, b in zip(path, path[1:]))
    return Route(region_id=region_id, waypoints=wps, est_duration_s=length / speed_mps,
                 est_battery_pct=length / 1000 * drain_pct_per_km)


def fits_battery(route: Route, battery_pct: float, reserve_pct: float = 20.0) -> bool:
    return route.est_battery_pct + reserve_pct <= battery_pct
