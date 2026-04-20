"""Redis-backed storage.

Install with ``pip install "captchakit[redis]"``. Uses native Redis key
expiration (``SETEX``) so expired challenges are cleaned up automatically
without polling.

Multi-process safe — well suited for multi-worker deployments (gunicorn,
uvicorn with ``--workers > 1``, Kubernetes pods, …) where
:class:`~captchakit.storage.memory.MemoryStorage` would silently lose state.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any

try:
    from redis.asyncio import Redis
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Redis storage requires the `redis` extra: pip install 'captchakit[redis]'"
    ) from exc

from captchakit._clock import Clock, MonotonicClock
from captchakit.challenges.base import Challenge


@dataclass(slots=True)
class RedisStorage:
    """Stores challenges in Redis using native TTL.

    Each challenge uses two keys:

    * ``<prefix>:ch:<id>`` — JSON-encoded challenge, expires at ``challenge.expires_at``.
    * ``<prefix>:att:<id>`` — attempt counter, same expiry.

    ``incr_attempts`` is a best-effort atomic check — it returns 0 if the
    challenge key was already evicted (by TTL or explicit ``delete``) at the
    moment of the call.
    """

    client: Redis
    prefix: str = "captchakit"
    clock: Clock = field(default_factory=MonotonicClock)
    # Grace window (seconds) added to Redis TTL so the manager gets a chance
    # to raise ChallengeExpired instead of Redis silently returning "not found".
    ttl_grace: float = 2.0

    def _ch_key(self, challenge_id: str) -> str:
        return f"{self.prefix}:ch:{challenge_id}"

    def _att_key(self, challenge_id: str) -> str:
        return f"{self.prefix}:att:{challenge_id}"

    def _ttl_seconds(self, expires_at: float) -> int:
        remaining = expires_at - self.clock.now() + self.ttl_grace
        return max(1, int(remaining) + 1)

    async def put(self, challenge: Challenge) -> None:
        ttl = self._ttl_seconds(challenge.expires_at)
        payload = json.dumps(asdict(challenge))
        async with self.client.pipeline(transaction=True) as pipe:
            pipe.set(self._ch_key(challenge.id), payload, ex=ttl)
            pipe.set(self._att_key(challenge.id), 0, ex=ttl)
            await pipe.execute()

    async def get(self, challenge_id: str) -> Challenge | None:
        raw: Any = await self.client.get(self._ch_key(challenge_id))
        if raw is None:
            return None
        data: dict[str, Any] = json.loads(raw)
        return Challenge(**data)

    async def delete(self, challenge_id: str) -> None:
        async with self.client.pipeline(transaction=True) as pipe:
            pipe.delete(self._ch_key(challenge_id))
            pipe.delete(self._att_key(challenge_id))
            await pipe.execute()

    async def incr_attempts(self, challenge_id: str) -> int:
        # Two-step: skip incrementing if the challenge key is already gone.
        # A Redis Lua script would be strictly atomic; this best-effort
        # version is good enough for the captcha use case (at worst a user
        # loses one attempt on a race with eviction).
        if not await self.client.exists(self._ch_key(challenge_id)):
            return 0
        result: Any = await self.client.incr(self._att_key(challenge_id))
        return int(result)
