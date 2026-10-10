"""Export JSON Schema for every contract (for the dashboard / non-Python consumers)."""
import json
import pathlib

from aerosentinel_schemas import models

out = pathlib.Path("docs/json_schema"); out.mkdir(exist_ok=True, parents=True)
for name in ("Observation", "Detection", "Measurement", "AnomalyEvent", "VerifiedAnomaly", "RiskScore",
             "Alert", "Route", "MissionRequest", "DroneState"):
    (out / f"{name}.json").write_text(json.dumps(getattr(models, name).model_json_schema(), indent=2))
print("wrote", out)
