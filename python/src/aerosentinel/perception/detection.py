"""D1: detectors. Everything returns `Detection` contracts so models are swappable."""
from __future__ import annotations

from typing import Protocol

from aerosentinel_schemas import Detection, HazardType, Observation


class Detector(Protocol):
    def detect(self, obs: Observation) -> list[Detection]: ...


class ThresholdDetector:
    """Baseline for scalar sensors: water level above a threshold => FLOOD."""
    version = "threshold-0.1"

    def __init__(self, water_level_m: float = 0.3) -> None:
        self.thr = water_level_m

    def detect(self, obs: Observation) -> list[Detection]:
        lvl = obs.readings.get("water_level_m", 0.0)
        if lvl < self.thr:
            return []
        conf = min(1.0, 0.5 + (lvl - self.thr) / 2)
        return [Detection(observation_id=obs.id, hazard=HazardType.FLOOD, confidence=conf,
                          geo=obs.position, model_version=self.version)]


class YoloDetector:
    """Image detector (flood / fire / smoke / landslide / cracks) on Ultralytics YOLO.

    Needs `pip install -e "python[ml]"`. Train with perception/train_yolo.py.
    """
    CLASS_TO_HAZARD = {"flood": HazardType.FLOOD, "fire": HazardType.FIRE, "smoke": HazardType.SMOKE,
                       "landslide": HazardType.LANDSLIDE, "crack": HazardType.STRUCTURAL_CRACK}

    def __init__(self, weights: str, conf: float = 0.25) -> None:
        from ultralytics import YOLO  # lazy: heavy import
        self.model, self.conf, self.version = YOLO(weights), conf, f"yolo:{weights}"

    def detect(self, obs: Observation) -> list[Detection]:
        if not obs.image_uri:
            return []
        out: list[Detection] = []
        for r in self.model.predict(obs.image_uri, conf=self.conf, verbose=False):
            for box in r.boxes:
                name = r.names[int(box.cls)]
                if name in self.CLASS_TO_HAZARD:
                    x, y, w, h = box.xywhn[0].tolist()
                    out.append(Detection(observation_id=obs.id, hazard=self.CLASS_TO_HAZARD[name],
                                         confidence=float(box.conf), bbox_xywh=(x, y, w, h),
                                         geo=obs.position, model_version=self.version))
        return out
