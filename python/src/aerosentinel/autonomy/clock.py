"""Time source. SimClock makes simulated days run in milliseconds; WallClock is for real flight."""
from __future__ import annotations

import time
from datetime import datetime, timedelta, timezone
from typing import Protocol


class Clock(Protocol):
    def now(self) -> datetime: ...
    def advance(self, td: timedelta) -> None: ...
    def sleep_until(self, t: datetime) -> None: ...


class SimClock:
    def __init__(self, start: datetime) -> None:
        self._now = start

    def now(self) -> datetime:
        return self._now

    def advance(self, td: timedelta) -> None:
        self._now += td

    def sleep_until(self, t: datetime) -> None:
        if t > self._now:
            self._now = t


class WallClock:
    def now(self) -> datetime:
        return datetime.now(timezone.utc)

    def advance(self, td: timedelta) -> None:  # real time advances by itself
        time.sleep(td.total_seconds())

    def sleep_until(self, t: datetime) -> None:
        time.sleep(max(0.0, (t - self.now()).total_seconds()))
