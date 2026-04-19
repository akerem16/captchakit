"""In-process storage backed by a dict and an asyncio lock."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field

from pycaptcha._clock import Clock, MonotonicClock
from pycaptcha.challenges.base import Challenge


@dataclass(slots=True)
class MemoryStorage:
    """Dict-based storage with a single :class:`asyncio.Lock`.

    Suitable for single-process deployments and tests. For multi-process
    setups (e.g. gunicorn with multiple workers) use a shared backend such as
    :class:`~pycaptcha.storage.redis.RedisStorage` (optional extra).
    """

    clock: Clock = field(default_factory=MonotonicClock)
    _data: dict[str, Challenge] = field(default_factory=dict, init=False)
    _attempts: dict[str, int] = field(default_factory=dict, init=False)
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock, init=False)

    async def put(self, challenge: Challenge) -> None:
        async with self._lock:
            self._data[challenge.id] = challenge
            self._attempts[challenge.id] = 0

    async def get(self, challenge_id: str) -> Challenge | None:
        async with self._lock:
            return self._data.get(challenge_id)

    async def delete(self, challenge_id: str) -> None:
        async with self._lock:
            self._data.pop(challenge_id, None)
            self._attempts.pop(challenge_id, None)

    async def incr_attempts(self, challenge_id: str) -> int:
        async with self._lock:
            if challenge_id not in self._data:
                return 0
            self._attempts[challenge_id] = self._attempts.get(challenge_id, 0) + 1
            return self._attempts[challenge_id]

    async def cleanup_expired(self) -> int:
        """Remove every challenge whose ``expires_at`` is in the past.

        Returns the number of entries evicted. Safe to call from a background
        task; intended to be scheduled periodically by the host application.
        """
        now = self.clock.now()
        async with self._lock:
            dead = [cid for cid, ch in self._data.items() if ch.is_expired(now)]
            for cid in dead:
                self._data.pop(cid, None)
                self._attempts.pop(cid, None)
            return len(dead)

    async def size(self) -> int:
        async with self._lock:
            return len(self._data)
