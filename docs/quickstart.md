# Quickstart

## 1. Install

```bash
pip install "captchakit[fastapi]"
```

## 2. Wire up a manager

```python
from captchakit import (
    CaptchaManager,
    ImageRenderer,
    MathChallengeFactory,
    MemoryStorage,
)

manager = CaptchaManager(
    factory=MathChallengeFactory(),
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
    ttl=120.0,         # seconds a challenge stays valid
    max_attempts=3,    # wrong answers before invalidation
)
```

## 3. Issue and verify

```python
challenge_id, png_bytes = await manager.issue()
# ...deliver png_bytes to the user, collect their answer...
try:
    ok = await manager.verify(challenge_id, "7")
except captchakit.ChallengeExpired:
    ...  # TTL elapsed
except captchakit.TooManyAttempts:
    ...  # user burned through their guesses
```

`verify` returns `True` on success, `False` while the user still has
attempts remaining. Specific failure modes raise typed exceptions.

## Choosing a challenge factory

| Factory | Output | Best for |
|---|---|---|
| `TextChallengeFactory` | random 5-char string | baseline |
| `MathChallengeFactory` | e.g. `"7 + 3 = ?"` | form sign-ups |
| `EmojiGridChallengeFactory` | grid + target emoji | Telegram/Discord inline buttons |
| `WordChallengeFactory` | real word from wordlist | accessibility-friendly |

## Choosing a storage backend

- **`MemoryStorage`** — single-process apps, tests. Fast, zero setup.
- **`RedisStorage`** — multi-worker deployments, horizontal scale. Native
  Redis TTL handles cleanup automatically. Opt-in via the `[redis]` extra.

```python
from redis.asyncio import Redis
from captchakit.storage import RedisStorage

storage = RedisStorage(client=Redis.from_url("redis://localhost:6379"))
```

## Next steps

- Integrate with your framework: [FastAPI](adapters/fastapi.md) ·
  [aiogram](adapters/aiogram.md) · [Discord](adapters/discord.md)
- Browse the [API reference](api.md).
