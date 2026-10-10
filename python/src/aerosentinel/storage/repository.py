"""Repository interface (A2). Modules depend on this Protocol, never on SQL.

`InMemoryRepository` is the default for tests and for the lightweight sim;
`PostgresRepository` (TODO, member 1) implements the same Protocol.
"""
from __future__ import annotations

from collections import defaultdict
from typing import Protocol

from aerosentinel_schemas import Alert, Observation, RiskScore


class Repository(Protocol):
    def add_observations(self, obs: list[Observation]) -> None: ...
    def observations(self, zone_id: str, *, sensor: str | None = None) -> list[Observation]: ...
    def add_risk(self, risk: RiskScore) -> None: ...
    def latest_risk(self, region_id: str) -> list[RiskScore]: ...
    def upsert_alert(self, alert: Alert) -> None: ...
    def open_alert_by_key(self, dedupe_key: str) -> Alert | None: ...
    def alerts(self, region_id: str) -> list[Alert]: ...


class InMemoryRepository:
    def __init__(self) -> None:
        self._obs: dict[str, list[Observation]] = defaultdict(list)
        self._risk: dict[tuple[str, str], RiskScore] = {}
        self._alerts: dict[str, Alert] = {}

    def add_observations(self, obs: list[Observation]) -> None:
        for o in obs:
            self._obs[o.zone_id].append(o)

    def observations(self, zone_id: str, *, sensor: str | None = None) -> list[Observation]:
        rows = sorted(self._obs[zone_id], key=lambda o: o.timestamp)
        return [o for o in rows if sensor is None or o.sensor == sensor]

    def add_risk(self, risk: RiskScore) -> None:
        self._risk[(risk.zone_id, risk.hazard)] = risk

    def latest_risk(self, region_id: str) -> list[RiskScore]:
        return [r for r in self._risk.values() if r.region_id == region_id]

    def upsert_alert(self, alert: Alert) -> None:
        self._alerts[alert.id] = alert

    def open_alert_by_key(self, dedupe_key: str) -> Alert | None:
        for a in self._alerts.values():
            if a.dedupe_key == dedupe_key and a.status != "resolved":
                return a
        return None

    def alerts(self, region_id: str) -> list[Alert]:
        return [a for a in self._alerts.values() if a.region_id == region_id]
