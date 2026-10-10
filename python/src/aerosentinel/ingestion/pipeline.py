"""A3: validate incoming drone payloads, reject bad rows, load good ones."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aerosentinel_schemas import Observation
from pydantic import ValidationError

from aerosentinel.storage.repository import Repository


@dataclass
class IngestReport:
    accepted: int = 0
    rejected: list[tuple[int, str]] = field(default_factory=list)  # (index, reason)


def ingest_observations(raw: list[dict[str, Any]], repo: Repository) -> IngestReport:
    report, good = IngestReport(), []
    for i, row in enumerate(raw):
        try:
            good.append(Observation.model_validate(row))
        except ValidationError as e:
            report.rejected.append((i, e.errors()[0]["msg"]))
    repo.add_observations(good)
    report.accepted = len(good)
    return report
