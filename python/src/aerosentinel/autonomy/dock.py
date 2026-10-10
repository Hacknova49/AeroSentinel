"""C2: dock & battery simulator. Decides readiness and charge duration."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta

from aerosentinel.autonomy.mock_drone import MockDrone


@dataclass
class DockSimulator:
    charge_pct_per_min: float = 2.0
    ready_pct: float = 95.0

    def is_ready(self, battery_pct: float) -> bool:
        return battery_pct >= self.ready_pct

    def recharge(self, drone: MockDrone) -> timedelta:
        """Charge the mock drone to full; advances the sim clock. Returns time spent."""
        need = 100.0 - drone.battery_level()
        dt = timedelta(minutes=need / self.charge_pct_per_min)
        drone.clock.advance(dt)
        drone._charge(need)
        return dt
