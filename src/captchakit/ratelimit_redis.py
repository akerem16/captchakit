"""Redis-backed token bucket for multi-process deployments.

Requires the ``[redis]`` extra. Uses a Lua script (atomic server-side
evaluation) so concurrent workers never over-issue.

Example::

    from redis.asyncio import Redis
    from captchakit import CaptchaManager
    from captchakit.ratelimit_redis import RedisTokenBucket

    bucket = RedisTokenBucket(Redis.from_url("redis://localhost:6379"))
    manager = CaptchaManager(..., rate_limiter=bucket)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

try:
    from redis.asyncio import Redis
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "RedisTokenBucket requires the `redis` extra: pip install 'captchakit[redis]'"
    ) from exc

from captchakit.errors import RateLimited

_LUA_SCRIPT = """
local key = KEYS[1]
local capacity = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])

local bucket = redis.call('HMGET', key, 'tokens', 'last')
local tokens = tonumber(bucket[1])
local last = tonumber(bucket[2])
if tokens == nil then
    tokens = capacity
    last = now
end
local delta = math.max(0, now - last)
tokens = math.min(capacity, tokens + delta * refill_rate)

local allowed = 0
local retry_after = 0
if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
else
    retry_after = (1 - tokens) / refill_rate
end

redis.call('HMSET', key, 'tokens', tokens, 'last', now)
redis.call('EXPIRE', key, math.ceil(capacity / refill_rate) + 10)
return {allowed, tostring(retry_after)}
"""


@dataclass(slots=True)
class RedisTokenBucket:
    """Token-bucket rate limiter backed by Redis + Lua.

    Safe across multiple workers / hosts. One key per caller id; keys
    are auto-expired by Redis once they become idle.
    """

    client: Redis
    capacity: float = 5.0
    refill_rate: float = 1.0
    prefix: str = "captchakit:rl"

    def __post_init__(self) -> None:
        if self.capacity <= 0:
            raise ValueError("capacity must be > 0")
        if self.refill_rate <= 0:
            raise ValueError("refill_rate must be > 0")

    async def acquire(self, key: str) -> None:
        import time  # noqa: PLC0415

        now = time.monotonic()
        redis_key = f"{self.prefix}:{key}"
        raw: Any = await self.client.eval(  # type: ignore[misc]
            _LUA_SCRIPT,
            1,
            redis_key,
            str(self.capacity),
            str(self.refill_rate),
            str(now),
        )
        allowed, retry_after_raw = raw
        if int(allowed) == 0:
            raise RateLimited(key, retry_after=float(retry_after_raw))


__all__ = ["RedisTokenBucket"]
