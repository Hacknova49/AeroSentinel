"""A4: FastAPI service. Run: uvicorn aerosentinel.api.app:app --reload  (OpenAPI at /docs)."""
from __future__ import annotations

from aerosentinel_schemas import SCHEMA_VERSION, Alert, RiskScore
from fastapi import FastAPI, WebSocket

from aerosentinel.storage.repository import InMemoryRepository, Repository


def create_app(repo: Repository | None = None) -> FastAPI:
    repo = repo or InMemoryRepository()
    app = FastAPI(title="AeroSentinel API", version=SCHEMA_VERSION)
    app.state.repo = repo

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok", "schema_version": SCHEMA_VERSION}

    @app.get("/regions/{region_id}/alerts", response_model=list[Alert])
    def alerts(region_id: str):
        return repo.alerts(region_id)

    @app.get("/regions/{region_id}/risk", response_model=list[RiskScore])
    def risk(region_id: str):
        return repo.latest_risk(region_id)

    @app.websocket("/ws/alerts")
    async def ws_alerts(ws: WebSocket):  # TODO(member 2): fan-out new alerts (Redis pub/sub or in-proc bus)
        await ws.accept()
        await ws.send_json({"info": "alert stream not implemented yet"})
        await ws.close()

    return app


app = create_app()
