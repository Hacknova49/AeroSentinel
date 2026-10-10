# Contracts (frozen set, section 1.2)
Source of truth: `packages/schemas/src/aerosentinel_schemas/models.py`. All models are immutable, reject unknown fields,
use WGS84 (`GeoPoint`, alt in metres AGL), timezone-aware UTC timestamps, and the IDs `region-xxx` / `region-xxx/z-yy`.

| Contract | Produced by | Consumed by |
|---|---|---|
| Observation | C1 drone `capture` | A3, D1, D3 |
| Detection | D1 | D2, D5 |
| Measurement | D2 | D5 |
| AnomalyEvent | D3 | C5, D5 |
| VerifiedAnomaly | C5 | D5 |
| RiskScore | D4 | D5, A4 |
| Alert | D5 | A4, E1 |
| Route | C4 | C3 |
| MissionRequest | C3 / operator | C4, C5 |
| DroneInterface | C1 implementations | C3, C5 |

Change process: see CONTRIBUTING.md. Python is canonical; export JSON Schema for the dashboard with
`python scripts/export_json_schema.py`.
