# Architecture notes
- **Sim parity ladder:** `MockDrone + FloodWorld` (B1, ms per patrol) -> `UnityDrone` (B3-B5) -> flight-stack adapter -> `RealDrone`.
  The e2e test in `integration/tests` runs the same pipeline at every rung.
- **Time:** `Clock` abstraction (`SimClock`/`WallClock`) lets months of patrols run in seconds in sim.
- **Data flow:** drone -> Observation -> ingestion -> repository -> detectors/trend/risk -> alert engine -> API -> dashboard.
- **Unity bridge:** TCP JSON-lines (see `autonomy/unity_drone.py`). Replaceable by ROS 2 without touching callers.
- **Sim-to-real note:** D1/D2/D4 train on Unity/synthetic data first; H8 retrains on field data. Keep dataset versioning from day one.
