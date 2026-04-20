"""Rate limiting hooks.

A :class:`RateLimiter` guards :meth:`~captchakit.CaptchaManager.issue`
so a single abusive client can't exhaust your server issuing millions
of challenges. The protocol is intentionally tiny — one ``acquire``
coroutine that raises :class:`~captchakit.errors.RateLimited` on
refusal — so you can plug in any bucket algorithm.

Two reference implementations ship with the core:

* :class:`NoOpRateLimiter` — default, always permits.
* :class:`TokenBucketRateLimiter` — in-memory token bucket, good for
  single-process deployments.

A Redis-backed variant lives in :mod:`captchakit.ratelimit_redis`
(``[redis]`` extra) for multi-process deployments.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from captchakit._clock import Clock, MonotonicClock
from captchakit.errors import RateLimited


@runtime_checkable
class RateLimiter(Protocol):
    """Decides whether an ``issue`` call is allowed to proceed.

    Implementations MUST be safe under concurrent async access from a
    single event loop. Multi-process safety is the backend's own
    responsibility.
    """

    async def acquire(self, key: str) -> None:
        """Permit one request from ``key``, or raise :class:`RateLimited`."""


class NoOpRateLimiter:
    """Default limiter — every call is permitted."""

    __slots__ = ()

    async def acquire(self, key: str) -> None:  # noqa: ARG002
        return None


@dataclass(slots=True)
class TokenBucketRateLimiter:
    """Classic token-bucket limiter, in-memory.

    Each key gets ``capacity`` tokens that refill at ``refill_rate``
    tokens per second. ``acquire`` consumes one token; if none are
    available, :class:`RateLimited` is raised with a ``retry_after``
    hint.

    Not multi-process safe — use the Redis variant when running more
    than one worker.
    """

    capacity: float = 5.0
    refill_rate: float = 1.0
    clock: Clock = field(default_factory=MonotonicClock)
    _buckets: dict[str, tuple[float, float]] = field(default_factory=dict, init=False)
    _locks: dict[str, asyncio.Lock] = field(
        default_factory=lambda: defaultdict(asyncio.Lock), init=False
    )

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("capacity must be > 0")
        if self.refill_rate <= 0:
            raise ValueError("refill_rate must be > 0")

    async def acquire(self, key: str) -> None:
        async with self._locks[key]:
            now = self.clock.now()
            tokens, last = self._buckets.get(key, (self.capacity, now))
            tokens = min(self.capacity, tokens + (now - last) * self.refill_rate)
            if tokens < 1:
                deficit = 1 - tokens
                retry_after = deficit / self.refill_rate
                self._buckets[key] = (tokens, now)
                raise RateLimited(key, retry_after=retry_after)
            self._buckets[key] = (tokens - 1, now)


__all__ = ["NoOpRateLimiter", "RateLimited", "RateLimiter", "TokenBucketRateLimiter"]
