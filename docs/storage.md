# Storage backends

All storage backends implement the `Storage` protocol (see
[API reference](api.md)):

```python
async def put(self, challenge: Challenge) -> None: ...
async def get(self, challenge_id: str) -> Challenge | None: ...
async def delete(self, challenge_id: str) -> None: ...
async def incr_attempts(self, challenge_id: str) -> int: ...
```

Swap in your own implementation (e.g. Postgres, Memcached, DynamoDB) by
writing four async methods — no subclassing required.

## `MemoryStorage`

```python
from captchakit import MemoryStorage

storage = MemoryStorage()
```

- In-process dict + `asyncio.Lock`.
- Fast, zero config.
- **Not** multi-process safe — use Redis once you run more than one worker.
- Provides an extra `cleanup_expired()` coroutine for periodic eviction.

## `RedisStorage`

```python
from redis.asyncio import Redis
from captchakit.storage import RedisStorage

client = Redis.from_url("redis://localhost:6379")
storage = RedisStorage(client=client, prefix="myapp")
```

- Async client (`redis.asyncio.Redis`).
- Two keys per challenge under `<prefix>:ch:<id>` and `<prefix>:att:<id>`.
- Native Redis TTL (`SETEX`) evicts expired challenges automatically — no
  background task required.
- Multi-process and multi-host safe; use this for any deployment with more
  than one worker.
- `incr_attempts` is best-effort atomic — if the challenge key was already
  evicted at the moment of the call, it returns 0.

### Opt-in

```bash
pip install "captchakit[redis]"
```

Until you install the extra, `from captchakit.storage import RedisStorage`
defers the underlying `redis` import — so the absence of the package never
breaks `from captchakit.storage import MemoryStorage`.
