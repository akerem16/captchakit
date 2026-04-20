# Rate limiting

`CaptchaManager.issue(key=...)` accepts a caller identifier and delegates
the quota decision to a `RateLimiter`. With the default
`NoOpRateLimiter` the key is ignored.

## `TokenBucketRateLimiter` (in-memory)

```python
from captchakit import (
    CaptchaManager,
    ImageRenderer,
    MemoryStorage,
    TextChallengeFactory,
    TokenBucketRateLimiter,
)

manager = CaptchaManager(
    factory=TextChallengeFactory(),
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
    rate_limiter=TokenBucketRateLimiter(capacity=5, refill_rate=1.0),
)

try:
    cid, png = await manager.issue(key=request.client.host)
except RateLimited as exc:
    # exc.retry_after is seconds until the next token
    ...
```

- `capacity` — max burst size (tokens).
- `refill_rate` — tokens added per second.
- One bucket per `key`.
- Single-process only.

## `RedisTokenBucket` (multi-process)

```python
from redis.asyncio import Redis
from captchakit import CaptchaManager
from captchakit.ratelimit_redis import RedisTokenBucket

bucket = RedisTokenBucket(
    client=Redis.from_url("redis://localhost:6379"),
    capacity=10,
    refill_rate=2.0,
)
manager = CaptchaManager(..., rate_limiter=bucket)
```

- Uses a Lua script (atomic server-side evaluation) so concurrent
  workers never over-issue.
- Install via the existing `[redis]` extra.
- Keys are auto-expired once they become idle.

## Custom limiter

`RateLimiter` is a `Protocol`. Any object with
`async def acquire(key: str) -> None` (raising
`RateLimited` on refusal) works:

```python
class AlwaysDeny:
    async def acquire(self, key: str) -> None:
        raise RateLimited(key)
```

Use this to wrap an existing app-wide limiter (Redis `INCR` + TTL,
`fastapi-limiter`, `slowapi`, a Cloudflare rule enforced at the edge,
…).

## Handling `RateLimited`

FastAPI:

```python
@app.exception_handler(RateLimited)
async def handle_rate_limited(request, exc: RateLimited) -> Response:
    return JSONResponse(
        {"error": "rate_limited", "retry_after": exc.retry_after},
        status_code=429,
        headers={"Retry-After": str(int(exc.retry_after or 1))},
    )
```
