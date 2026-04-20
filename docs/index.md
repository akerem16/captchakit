# captchakit

**Async-first, fully type-hinted, minimal captcha library for Python 3.10+.**
Zero runtime dependencies beyond Pillow. Drop-in adapters for FastAPI,
aiogram and discord.py.

## Why

Most Python captcha libraries stop at "render a PNG" — no TTL, no attempt
tracking, no async, partial type hints, and no framework glue. captchakit
gives you a small modern SDK that handles the whole issue → verify →
expire flow, and ships adapters so you're wired into your framework in a
single line.

## At a glance

| | `lepture/captcha` | `claptcha` | `multicolorcaptcha` | **captchakit** |
|---|---|---|---|---|
| Async API | ❌ | ❌ | ❌ | ✅ |
| `py.typed` + mypy strict | ⚠️ | ❌ | ❌ | ✅ |
| TTL & attempt tracking | ❌ | ❌ | ❌ | ✅ built-in |
| Pluggable storage | ❌ | ❌ | ❌ | ✅ `Protocol` |
| Framework adapters | ❌ | ❌ | ❌ | ✅ FastAPI · aiogram · discord.py |

## 30-second example

```python
import asyncio
from captchakit import (
    CaptchaManager, ImageRenderer, MemoryStorage, TextChallengeFactory,
)

async def main() -> None:
    manager = CaptchaManager(
        factory=TextChallengeFactory(length=5),
        renderer=ImageRenderer(),
        storage=MemoryStorage(),
        ttl=120.0,
        max_attempts=3,
    )
    challenge_id, png_bytes = await manager.issue()
    # ... show png_bytes to the user, receive their answer ...
    ok = await manager.verify(challenge_id, user_input="ABCDE")
    print("verified" if ok else "wrong answer, more attempts remain")

asyncio.run(main())
```

## Install

```bash
pip install captchakit                 # core
pip install "captchakit[fastapi]"      # + FastAPI adapter
pip install "captchakit[aiogram]"      # + aiogram adapter
pip install "captchakit[discord]"      # + discord.py adapter
pip install "captchakit[redis]"        # + Redis storage backend
```

## Security scope

captchakit is a **lightweight human-check**, not a bot-farm-grade security
layer. For high-value surfaces (login, payment, password reset) use
hCaptcha / Cloudflare Turnstile / reCAPTCHA Enterprise in addition. See
[SECURITY.md](https://github.com/akerem16/captchakit/blob/main/SECURITY.md)
for the full threat model.
