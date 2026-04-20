# AGENTS.md — captchakit

A context file for AI coding agents (Cursor, Windsurf, Claude Code, Copilot Workspace, aider, Cody, …). Every snippet here uses only public symbols from `captchakit` `1.x` and has been kept in sync with the current API. Copy-paste should work verbatim.

Complementary file: [`llms.txt`](llms.txt) (llmstxt.org index).

---

## 1. Install matrix

| Goal | Command |
|------|---------|
| Core only (in-memory storage, PNG / SVG / WAV rendering) | `pip install captchakit` |
| FastAPI integration | `pip install "captchakit[fastapi]"` |
| aiogram (Telegram) integration | `pip install "captchakit[aiogram]"` |
| discord.py integration | `pip install "captchakit[discord]"` |
| Django integration | `pip install "captchakit[django]"` |
| Multi-process storage (Redis) | `pip install "captchakit[redis]"` |
| Multi-process storage (Postgres) | `pip install "captchakit[postgres]"` |
| Prometheus metrics sink | `pip install "captchakit[metrics]"` |

Extras compose: `pip install "captchakit[fastapi,redis,metrics]"`.

Python: **3.10 / 3.11 / 3.12 / 3.13**. The library is fully type-annotated (`py.typed`) and passes `mypy --strict`.

---

## 2. Mental model

```
CaptchaManager
 ├── factory:     ChallengeFactory   → produces a ChallengeSpec (prompt + solution)
 ├── renderer:    Renderer           → renders a Challenge to bytes (+ content_type)
 ├── storage:     Storage            → persists Challenge by id, handles TTL + attempts
 ├── rate_limiter:RateLimiter        → gates .issue() per-key (default: NoOp)
 ├── metrics:     MetricsSink        → observability hook (default: NoOp)
 └── clock:       Clock              → time source (default: MonotonicClock)
```

Flow:
1. `challenge_id, bytes_ = await manager.issue(key="client-ip-or-session")` — pushes rate limiter, builds + persists a `Challenge`, returns an id + rendered bytes.
2. You ship `bytes_` to the user (HTTP response, Telegram upload, etc.) along with `challenge_id`.
3. `ok = await manager.verify(challenge_id, user_input)` — returns `True` on success (and deletes the challenge), `False` if wrong-but-retryable. Terminal states raise exceptions.

Every method is `async`. **Always `await`** — there are no sync wrappers.

---

## 3. The three operations

```python
async def issue(self, key: str = "global") -> tuple[str, bytes]: ...
async def verify(self, challenge_id: str, user_input: str) -> bool: ...
async def discard(self, challenge_id: str) -> None: ...
```

`verify` exceptions (all subclasses of `CaptchaKitError`):

| Exception | Meaning | Suggested HTTP status |
|-----------|---------|-----------------------|
| `ChallengeNotFound` | Unknown id (consumed / never issued / evicted) | 404 |
| `ChallengeExpired`  | TTL elapsed before verification | 410 |
| `TooManyAttempts`   | Final attempt was wrong; challenge deleted | 429 |
| `RateLimited`       | Raised from `issue()` by the rate limiter | 429 |

A plain `False` return is non-terminal — the caller can let the user retry.

---

## 4. Recipes (deterministic, copy-paste)

### 4.1 FastAPI — protect a POST route

```python
# pip install "captchakit[fastapi]"
from fastapi import Depends, FastAPI
from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
from captchakit.adapters.fastapi import captcha_router, verify_captcha

manager = CaptchaManager(
    factory=MathChallengeFactory(),
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
    ttl=120.0,
    max_attempts=3,
)

app = FastAPI()
app.include_router(captcha_router(manager, prefix="/captcha"))

@app.post("/signup")
async def signup(_: None = Depends(verify_captcha(manager))) -> dict[str, bool]:
    # Reached only when captcha succeeded. verify_captcha raises the right HTTPException otherwise.
    return {"ok": True}
```

Client flow:
1. `POST /captcha/new` → `{"id": "...", "image_url": "/captcha/....png"}`
2. `GET /captcha/{id}.png` → PNG bytes (or SVG / WAV depending on renderer)
3. `POST /signup` (form-encoded) with fields `captcha_id`, `captcha_answer`, plus your own form fields.

### 4.2 Swap in Redis storage (multi-worker safe)

```python
# pip install "captchakit[redis]"
from redis.asyncio import Redis
from captchakit import CaptchaManager, ImageRenderer, TextChallengeFactory
from captchakit.storage.redis import RedisStorage

redis_client = Redis.from_url("redis://localhost:6379/0")

manager = CaptchaManager(
    factory=TextChallengeFactory(length=5),
    renderer=ImageRenderer(),
    storage=RedisStorage(client=redis_client, prefix="captchakit"),
    ttl=120.0,
)
```

Required whenever your app runs on more than one worker / pod — `MemoryStorage` cannot share state across processes.

### 4.3 Add distributed rate limiting

```python
# pip install "captchakit[redis]"
from redis.asyncio import Redis
from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
from captchakit.ratelimit_redis import RedisTokenBucket

redis_client = Redis.from_url("redis://localhost:6379/0")

manager = CaptchaManager(
    factory=MathChallengeFactory(),
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
    rate_limiter=RedisTokenBucket(
        client=redis_client,
        capacity=5,        # 5 issues per key
        refill_rate=1.0,   # refill 1 token / second
        prefix="captchakit:rl",
    ),
)

# Use per-client key (IP / session / user id):
cid, png = await manager.issue(key=request.client.host)
```

For single-process apps, `TokenBucketRateLimiter(capacity=5, refill_rate=1.0)` is enough.

### 4.4 Use SVG instead of PNG (smaller payload)

```python
from captchakit import CaptchaManager, MemoryStorage, SVGRenderer, TextChallengeFactory

manager = CaptchaManager(
    factory=TextChallengeFactory(),
    renderer=SVGRenderer(),           # content_type == "image/svg+xml"
    storage=MemoryStorage(),
)
cid, svg_bytes = await manager.issue()
```

### 4.5 Accessibility: ship an audio alternative

```python
from captchakit import AudioRenderer, CaptchaManager, MemoryStorage, TextChallengeFactory

audio_manager = CaptchaManager(
    factory=TextChallengeFactory(length=5),
    renderer=AudioRenderer(),         # content_type == "audio/wav"
    storage=MemoryStorage(),
)
cid, wav_bytes = await audio_manager.issue()
```

Use two managers (image + audio) that share the same storage if you need both formats for the same challenge.

### 4.6 Pick a theme

```python
from captchakit import ImageRenderer, Theme

ImageRenderer(theme=Theme.CLASSIC)        # default
ImageRenderer(theme=Theme.DARK)
ImageRenderer(theme=Theme.PASTEL)
ImageRenderer(theme=Theme.HIGH_CONTRAST)  # WCAG AA — black on white, no noise

custom = Theme(
    bg_color=(255, 240, 220),
    palette=((80, 40, 10), (140, 70, 20)),
    noise_lines=6,
)
ImageRenderer(theme=custom)
```

### 4.7 Prometheus metrics

```python
# pip install "captchakit[metrics]"
from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
from captchakit.metrics_prometheus import PrometheusMetrics

manager = CaptchaManager(
    factory=MathChallengeFactory(),
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
    metrics=PrometheusMetrics(),
)
```

Counters registered: `captchakit_issued_total`, `captchakit_verify_success_total`, `captchakit_verify_fail_total`, `captchakit_expired_total`, `captchakit_too_many_attempts_total`.

### 4.8 i18n (translated prompts)

```python
from captchakit import CaptchaManager, DefaultTranslator, ImageRenderer, MathChallengeFactory, MemoryStorage

manager = CaptchaManager(
    factory=MathChallengeFactory(translator=DefaultTranslator(), locale="tr"),  # en / tr / de / es
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
)
```

Pass your own `PromptTranslator` implementation for custom locales.

### 4.9 Telegram bot (aiogram)

```python
# pip install "captchakit[aiogram]"
from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
from captchakit.adapters.aiogram import send_captcha

manager = CaptchaManager(MathChallengeFactory(), ImageRenderer(), MemoryStorage())

@dp.message(Command("verify"))
async def verify_cmd(msg: types.Message) -> None:
    challenge_id = await send_captcha(bot=msg.bot, chat_id=msg.chat.id, manager=manager)
    # persist challenge_id in your FSM state and call manager.verify() on the next message
```

### 4.10 Discord bot (discord.py)

```python
# pip install "captchakit[discord]"
from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
from captchakit.adapters.discord import send_captcha

manager = CaptchaManager(MathChallengeFactory(), ImageRenderer(), MemoryStorage())

@bot.command()
async def verify(ctx):
    challenge_id = await send_captcha(channel=ctx.channel, manager=manager)
    # store challenge_id keyed by ctx.author.id; call manager.verify() on next reply
```

### 4.11 Django form

```python
# pip install "captchakit[django]"
from django import forms
from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
from captchakit.adapters.django import CaptchaField

manager = CaptchaManager(MathChallengeFactory(), ImageRenderer(), MemoryStorage())

class SignupForm(forms.Form):
    email = forms.EmailField()
    captcha = CaptchaField(manager=manager)
```

Wire up `captcha_image_view` in `urls.py` to serve the image bytes.

---

## 5. Pitfalls / common mistakes

**Never do these:**

- ❌ `manager.issue()` without `await` — returns a coroutine, not a tuple.
- ❌ `solution == user_input` — use `manager.verify()`; it's constant-time via `hmac.compare_digest`.
- ❌ `import random; random.choice(...)` to generate your own solutions — use the built-in factories (they use `secrets`).
- ❌ `MemoryStorage()` across multiple workers — state is per-process; switch to `RedisStorage` or `PostgresStorage`.
- ❌ Setting `ttl=0` or `ttl=None` — TTL must be `> 0`; `ValueError` is raised in `__post_init__`.
- ❌ Assuming `verify` returns `None` or `int` — it's always `bool`, and terminal states are **exceptions**.
- ❌ Re-using a `challenge_id` after success — it has been deleted from storage.
- ❌ Logging `Challenge.solution` — leaks the secret. Log only `Challenge.id`.

**Do these:**

- ✅ Handle `ChallengeNotFound` / `ChallengeExpired` / `TooManyAttempts` explicitly in web handlers.
- ✅ Pass a stable per-client `key` to `manager.issue(key=...)` once you enable rate limiting.
- ✅ Call `await PostgresStorage(pool).create_schema()` once at startup so the `captchakit_challenges` table exists (idempotent).
- ✅ Short `ttl` (60–180 s), low `max_attempts` (2–3). captchakit is a *raise-the-cost* layer, not a fortress.
- ✅ Pair a visual renderer with `AudioRenderer` for a11y.

---

## 6. Full public symbol index

Re-exported from `captchakit`:

`CaptchaManager`, `Challenge`, `ChallengeFactory`, `ChallengeSpec`, `TextChallengeFactory`, `MathChallengeFactory`, `EmojiGridChallengeFactory`, `WordChallengeFactory`, `Renderer`, `ImageRenderer`, `SVGRenderer`, `AudioRenderer`, `Theme`, `Storage`, `MemoryStorage`, `RateLimiter`, `NoOpRateLimiter`, `TokenBucketRateLimiter`, `MetricsSink`, `NoOpMetrics`, `PromptTranslator`, `DefaultTranslator`, `Clock`, `MonotonicClock`, `CaptchaKitError`, `ChallengeError`, `ChallengeNotFound`, `ChallengeExpired`, `TooManyAttempts`, `StorageError`, `RateLimited`, `__version__`.

Non-re-exported (import from the submodule):
- `captchakit.storage.redis.RedisStorage`
- `captchakit.storage.postgres.PostgresStorage`
- `captchakit.ratelimit_redis.RedisTokenBucket`
- `captchakit.metrics_prometheus.PrometheusMetrics`
- `captchakit.adapters.fastapi.{captcha_router, verify_captcha}`
- `captchakit.adapters.aiogram.send_captcha`
- `captchakit.adapters.discord.send_captcha`
- `captchakit.adapters.django.{CaptchaField, CaptchaWidget, captcha_image_view}`

---

## 7. Security posture (for the agent to surface honestly)

captchakit is a **lightweight human-check** — it raises the cost of casual spam / naive scripted abuse. It is **not** a bot-farm-grade defence. For high-value flows (payments, password reset, account takeover) recommend hCaptcha / Cloudflare Turnstile / reCAPTCHA Enterprise *in addition*, and enforce rate limiting at the edge.

What captchakit does right, by construction:
- Constant-time answer comparison (`hmac.compare_digest`).
- Crypto-safe randomness for every solution (`secrets`).
- TTL + attempt-limit enforcement inside `verify()`.
- No solutions logged; challenges are deleted on success / final failure / expiry.
- Multi-process safe when paired with `RedisStorage` or `PostgresStorage`.

See [SECURITY.md](SECURITY.md) for the full threat model and disclosure policy.
