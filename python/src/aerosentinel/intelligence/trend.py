"""D3: trend & anomaly detection on per-zone time series."""
from __future__ import annotations

import numpy as np
from aerosentinel_schemas import AnomalyEvent, utcnow


def zscore_latest(series: list[float], window: int = 30) -> float:
    """z-score of the last value against the preceding window."""
    if len(series) < 3:
        return 0.0
    hist = np.asarray(series[-window - 1:-1])
    sd = hist.std() or 1e-9
    return float((series[-1] - hist.mean()) / sd)


def cusum_change(series: list[float], k: float = 0.5, h: float = 5.0) -> bool:
    """One-sided CUSUM for upward drift (accelerating change)."""
    x = np.asarray(series)
    if len(x) < 5:
        return False
    z = (x - x[: max(3, len(x) // 2)].mean()) / (x[: max(3, len(x) // 2)].std() or 1e-9)
    s = 0.0
    for v in z:
        s = max(0.0, s + v - k)
        if s > h:
            return True
    return False


def detect_anomalies(region_id: str, zone_id: str, metric: str, series: list[float],
                     z_thr: float = 3.0) -> list[AnomalyEvent]:
    events = []
    z = zscore_latest(series)
    if abs(z) >= z_thr:
        events.append(AnomalyEvent(region_id=region_id, zone_id=zone_id, metric=metric, method="zscore",
                                   score=z, timestamp=utcnow()))
    if cusum_change(series):
        events.append(AnomalyEvent(region_id=region_id, zone_id=zone_id, metric=metric, method="cusum",
                                   score=1.0, timestamp=utcnow(), note="sustained upward drift"))
    return events


def fit_isolation_forest(X: np.ndarray, contamination: float = 0.02):
    from sklearn.ensemble import IsolationForest  # needs the [ml] extra
    return IsolationForest(contamination=contamination, random_state=0).fit(X)
