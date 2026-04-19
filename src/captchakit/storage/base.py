"""Storage protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from captchakit.challenges.base import Challenge


@runtime_checkable
class Storage(Protocol):
    """Persists challenges while they are live.

    Implementations MUST be safe under concurrent async access from a single
    event loop. Multi-process safety is the backend's own responsibility
    (e.g. Redis is multi-process-safe; in-memory is not).
    """

    async def put(self, challenge: Challenge) -> None:  # pragma: no cover - protocol
        ...

    async def get(self, challenge_id: str) -> Challenge | None:  # pragma: no cover - protocol
        ...

    async def delete(self, challenge_id: str) -> None:  # pragma: no cover - protocol
        ...

    async def incr_attempts(self, challenge_id: str) -> int:  # pragma: no cover - protocol
        ...
