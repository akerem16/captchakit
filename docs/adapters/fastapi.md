# FastAPI adapter

Install: `pip install "captchakit[fastapi]"`.

## Router + dependency

```python
from fastapi import Depends, FastAPI
from captchakit import (
    CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage,
)
from captchakit.adapters.fastapi import captcha_router, verify_captcha

manager = CaptchaManager(
    MathChallengeFactory(), ImageRenderer(), MemoryStorage(),
)
app = FastAPI()
app.include_router(captcha_router(manager, prefix="/captcha"))

@app.post("/register")
async def register(_: None = Depends(verify_captcha(manager))) -> dict[str, bool]:
    return {"ok": True}
```

## Exposed endpoints

| Method | Path | Body / Response |
|---|---|---|
| `POST` | `{prefix}/new` | `{"id": str, "image_url": str}` |
| `GET` | `{prefix}/{id}.png` | PNG bytes (`image/png`) |
| `POST` | `{prefix}/verify` | form `id`, `answer` → `{"ok": bool}` |

## `verify_captcha` dependency

Expects two form fields on the protected route:

- `captcha_id` — the id returned by `/new`
- `captcha_answer` — the user's answer

On failure, it raises a typed `HTTPException`:

| Exception | Status |
|---|---|
| `ChallengeNotFound` | 404 |
| `ChallengeExpired` | 410 |
| `TooManyAttempts` | 429 |
| (wrong answer, still has attempts) | 403 |

## Full demo

See `examples/fastapi_login.py` in the repo — run with:

```bash
uv run python -m uvicorn examples.fastapi_login:app --reload
```
