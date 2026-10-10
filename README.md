# AeroSentinel

Autonomous drone-based disaster monitoring and early-warning system. Template monorepo for **Plan 1 (Software)**:
21 modules in 5 layers, Unity 3D simulation, Python / PyTorch for ML.

```
                +-----------------------------------------------+
  Unity 3D  --> |  DroneInterface  (MockDrone | UnityDrone | ...) | <-- RealDrone (Plan 2)
  B3 B4 B5      +----------------------+------------------------+
                     C3 scheduler / C4 planner / C5 investigation
                                       | Observation
                  A3 ingestion -> A2 storage -> D1 detect -> D2 measure
                                       |            D3 trend -> D4 risk
                                       v                  \-> D5 alerts -> A4 API -> E1 dashboard
```

## Quick start
```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
make install            # schemas + python package + dev tools (no heavy ML deps)
make test               # unit tests + end-to-end smoke test
make demo               # one simulated patrol in the 2D geo-sim -> alert printed
make api                # FastAPI on :8000  (OpenAPI at /docs)
make install-ml         # torch, ultralytics, opencv, sklearn, xgboost (for D1/D3/D4 work)
```
Unity: see [`unity/AeroSentinel/README.md`](unity/AeroSentinel/README.md). Full stack: `docker compose up`.

## Layout
| Path | Modules | Owner |
|---|---|---|
| `packages/schemas/` | A1 contracts + `DroneInterface` (`aerosentinel-schemas`, versioned) | 1 |
| `python/src/aerosentinel/storage/` | A2 migrations (PostGIS/Timescale) + repository | 1 |
| `python/src/aerosentinel/ingestion/` | A3 | 1 |
| `python/src/aerosentinel/api/` | A4 FastAPI | 2 |
| `python/src/aerosentinel/geosim/`, `datagen/` | B1, B2 | 4 |
| `unity/AeroSentinel/` | B3, B4, B5 (+ Unity side of C1) | 5 |
| `python/src/aerosentinel/autonomy/` | C1-C4 (member 6), C5 (member 7) | 6 / 7 |
| `python/src/aerosentinel/perception/` | D1, D2 | 7 |
| `python/src/aerosentinel/intelligence/` | D3, D4, D5 | 8 |
| `dashboard/` | E1 React + Mapbox/Cesium | 3 |
| `integration/`, `docker-compose.yml`, `.github/` | E2 | 2 |

Ownership with backups: [`OWNERS.md`](OWNERS.md). Module-by-module status and TODOs: [`docs/modules.md`](docs/modules.md).

## Working principles (from the module breakdown)
1. **Contracts first.** `packages/schemas` is frozen before implementation; changes need review from dependent module owners (see `CODEOWNERS`).
2. **One boundary to the drone.** Only `DroneInterface` touches a drone. Sim to real is a config change.
3. **Build against mocks.** Every module can run with `MockDrone` + `FloodWorld` + `InMemoryRepository`, no Unity or DB needed.
4. **Primary + backup owner** per module. **Integration owner** (member 2) keeps `integration/tests` green on every merge.
5. Conventions: WGS84, UTC (naive datetimes are rejected), `region-xxx` and `region-xxx/z-yy` identifiers.
