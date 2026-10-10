"""D5: fuse detections + risk into alerts; de-duplicate by zone+hazard; escalate, never silently downgrade."""
from __future__ import annotations

from aerosentinel_schemas import Alert, Detection, Measurement, RiskScore, Severity, utcnow

from aerosentinel.storage.repository import Repository

_ORDER = [Severity.INFO, Severity.WATCH, Severity.WARNING, Severity.CRITICAL]


class AlertEngine:
    def __init__(self, repo: Repository, risk_watch: float = 0.4, risk_warning: float = 0.7) -> None:
        self.repo, self.risk_watch, self.risk_warning = repo, risk_watch, risk_warning

    def _upsert(self, region_id, zone_id, hazard, severity, *, verified, risk, message) -> Alert:
        now, key = utcnow(), f"{zone_id}:{hazard.value}"
        existing = self.repo.open_alert_by_key(key)
        if existing is None:
            alert = Alert(dedupe_key=key, region_id=region_id, zone_id=zone_id, hazard=hazard, severity=severity,
                          verified=verified, risk_score=risk, message=message, created_at=now, updated_at=now)
        else:
            sev = max(existing.severity, severity, key=_ORDER.index)   # escalate only
            alert = existing.model_copy(update={
                "severity": sev, "verified": existing.verified or verified, "updated_at": now,
                "risk_score": risk if risk is not None else existing.risk_score,
                "message": message if sev == severity else existing.message})
        self.repo.upsert_alert(alert)
        return alert

    def on_detection(self, det: Detection, region_id: str, zone_id: str, *, verified: bool = False,
                     measurement: Measurement | None = None) -> Alert:
        if verified:
            sev = Severity.CRITICAL if measurement and measurement.value >= 1.0 else Severity.WARNING
        else:
            sev = Severity.WATCH
        depth = f" depth {measurement.value:.2f} {measurement.unit}" if measurement else ""
        return self._upsert(region_id, zone_id, det.hazard, sev, verified=verified, risk=None,
                            message=f"{det.hazard.value} detected (conf {det.confidence:.2f}){depth}")

    def on_risk(self, risk: RiskScore) -> Alert | None:
        if risk.score >= self.risk_warning:
            sev = Severity.WARNING
        elif risk.score >= self.risk_watch:
            sev = Severity.WATCH
        else:
            return None
        return self._upsert(risk.region_id, risk.zone_id, risk.hazard, sev, verified=False, risk=risk.score,
                            message=f"{risk.hazard.value} risk {risk.score:.2f} within {risk.horizon_hours}h")
