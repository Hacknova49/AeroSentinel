"""D2: severity quantification. TODO(member 7): segmentation-based area / depth-from-reference."""
from __future__ import annotations

from aerosentinel_schemas import Detection, HazardType, Measurement, Observation


def measure(det: Detection, obs: Observation) -> Measurement | None:
    if det.hazard is HazardType.FLOOD and "water_level_m" in obs.readings:
        return Measurement(detection_id=det.id, metric="water_depth", value=obs.readings["water_level_m"],
                           unit="m", uncertainty=0.05)
    return None
