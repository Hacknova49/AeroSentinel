# Unity project (B3, B4, B5, Unity side of C1)

Unity owns the 3D world, disaster events and virtual sensors. Python owns everything else and drives Unity
through `UnityDrone` (TCP bridge, JSON lines, default port 5555) - the same `DroneInterface` as `MockDrone`.

## First-time setup
1. In Unity Hub create a **3D (URP)** project in an empty temp folder (Unity 6 LTS or your team's pinned version).
2. Copy its `Packages/` and `ProjectSettings/` into this folder, then commit them. Pin the version in `ProjectSettings/ProjectVersion.txt`.
3. Package Manager -> add `com.unity.nuget.newtonsoft-json`.
4. Open a scene and add the components listed in `Assets/AeroSentinel/World/README.md`.
5. Press Play, then from the repo root: `python scripts/run_unity_demo.py`.

The C# scripts were written without a Unity compile pass; expect a few small fixes on first import.
