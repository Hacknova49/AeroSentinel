# ADR-0004: Unity <-> Python bridge (ACCEPTED, revisit with ADR-0001)
TCP JSON-lines server inside Unity (`DroneBridgeServer.cs`), `UnityDrone` client in Python. Chosen for zero extra dependencies.
Images are written to disk by Unity and referenced by `image_uri` (shared path/volume), not sent over the socket.
