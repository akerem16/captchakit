# captchakit

> **Async-first, fully type-hinted captcha library for Python 3.10+.**
> Zero runtime deps beyond Pillow. Drop-in adapters for FastAPI, aiogram and discord.py.

[![PyPI](https://img.shields.io/badge/pypi-v0.2.0-blue.svg)](https://pypi.org/project/captchakit/)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://pypi.org/project/captchakit/)
[![CI](https://github.com/akerem16/captchakit/actions/workflows/ci.yml/badge.svg)](https://github.com/akerem16/captchakit/actions/workflows/ci.yml)
[![mypy: strict](https://img.shields.io/badge/mypy-strict-blue.svg)](http://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

## Why another one?

| Feature                  | `lepture/captcha` | `claptcha` | `multicolorcaptcha` | **captchakit**                    |
| ------------------------ | ----------------- | ---------- | ------------------- | --------------------------------- |
| Async API                | ❌                 | ❌          | ❌                   | ✅                                 |
| `py.typed` + mypy strict | ⚠️                | ❌          | ❌                   | ✅                                 |
| TTL & attempt tracking   | ❌                 | ❌          | ❌                   | ✅ built-in                        |
| Pluggable storage        | ❌                 | ❌          | ❌                   | ✅ `Protocol`                      |
| Framework adapters       | ❌                 | ❌          | ❌                   | ✅ FastAPI · aiogram · discord.py |
| Runtime deps (core)      | +Pillow           | +Pillow    | +Pillow             | +Pillow                           |

## Install

```bash
pip install captchakit                  # core
pip install "captchakit[fastapi]"       # + FastAPI adapter
pip install "captchakit[aiogram]"       # + aiogram adapter
pip install "captchakit[discord]"       # + discord.py adapter (coming in 0.3)
pip install "captchakit[redis]"         # + Redis storage backend
```

> `discord.py` adapter lands in 0.3 — its extra installs today but the
> adapter module itself is not yet shipped. See [ROADMAP.md](ROADMAP.md).

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

## FastAPI in 10 lines

```python
from fastapi import Depends, FastAPI
from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
from captchakit.adapters.fastapi import captcha_router, verify_captcha

manager = CaptchaManager(MathChallengeFactory(), ImageRenderer(), MemoryStorage())
app = FastAPI()
app.include_router(captcha_router(manager, prefix="/captcha"))

@app.post("/register")
async def register(_: None = Depends(verify_captcha(manager))) -> dict[str, bool]:
    return {"ok": True}
```

Run the bundled demo:

```bash
uv run python -m uvicorn examples.fastapi_login:app --reload
# open http://127.0.0.1:8000
```

## Design

```
┌─────────────────────────────────────────────────┐
│  Adapters (fastapi / aiogram / discord)         │
├─────────────────────────────────────────────────┤
│  CaptchaManager  (public facade)                │
├──────────────┬──────────────┬───────────────────┤
│  Challenge   │  Renderer    │  Storage          │
│  Text / Math │  Image (PIL) │  Memory / Redis   │
└──────────────┴──────────────┴───────────────────┘
```

- **`Protocol`-based**, so you can drop in your own storage (Redis, Postgres,
  Memcached), your own renderer (SVG, WebP, audio), or your own challenge
  factory (wordlists, emoji grids, …).
- **Constant-time comparison** via `hmac.compare_digest`.
- **Crypto-safe randomness** via `secrets` for solution generation.
- **CPU-bound Pillow drawing** offloaded to a worker thread via
  `asyncio.to_thread`, so the event loop never blocks.

## Security scope

**captchakit is a lightweight human-check**, not a bot-farm-grade security layer.
It is aimed at Telegram/Discord verification, simple FastAPI registration flows
and similar use cases where you just want to raise the cost for casual spam.

For high-value forms (login, payment) use **hCaptcha**, **Cloudflare Turnstile**
or **reCAPTCHA Enterprise** in addition. Combine captchakit with proper rate
limiting at the edge of your application.

## Roadmap

See [ROADMAP.md](ROADMAP.md) for the full development plan.

| Version | Highlights |
|---|---|
| 0.1 (MVP) | Core + Text/Math challenges + Image renderer + Memory storage + FastAPI |
| 0.2 ✅ | aiogram adapter + RedisStorage + EmojiGridChallenge |
| 0.3 | discord.py adapter + AudioChallenge (optional) + WordChallenge + docs site |
| 0.4 | i18n + theming + metrics hooks |
| 1.0 | Stable API, semver commitment |

## Contributing

Contributions welcome. Local development:

```bash
git clone https://github.com/akerem16/captchakit
cd captchakit
uv sync --all-extras
uv run ruff check .
uv run mypy
uv run pytest
```

## License

MIT — see [LICENSE](LICENSE).
