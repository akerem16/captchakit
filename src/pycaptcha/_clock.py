"""Time abstraction so tests can inject deterministic clocks."""

from __future__ import annotations

import time
from typing import Protocol, runtime_checkable


@runtime_checkable
class Clock(Protocol):
    """Minimal monotonic-time interface."""

    def now(self) -> float:  # pragma: no cover - protocol
        ...


class MonotonicClock:
    """Default clock backed by :func:`time.monotonic`."""

    __slots__ = ()

    def now(self) -> float:
        return time.monotonic()
