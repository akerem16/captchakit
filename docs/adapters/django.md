# Django

```bash
pip install "captchakit[django]"
```

Django is sync-first, so the adapter bridges `CaptchaManager`'s async API
through `asgiref.sync.async_to_sync`.

## Setup

Keep a single module-level manager — reuse it across views and forms:

```python
# app/captcha.py
from captchakit import (
    CaptchaManager,
    ImageRenderer,
    MemoryStorage,
    TextChallengeFactory,
)

manager = CaptchaManager(
    factory=TextChallengeFactory(length=5),
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
    ttl=180.0,
)
```

> Use `RedisStorage` or `PostgresStorage` if you run more than one
> worker — `MemoryStorage` can't share challenges across processes.

## Image view

```python
# urls.py
from django.urls import path
from captchakit.adapters.django import captcha_image_view
from app.captcha import manager

urlpatterns = [
    path("captcha/<str:challenge_id>.png", captcha_image_view(manager)),
]
```

## Form field

```python
from django import forms
from captchakit.adapters.django import CaptchaField
from app.captcha import manager

class RegisterForm(forms.Form):
    username = forms.CharField()
    captcha = CaptchaField(manager=manager)
```

- Issues a fresh challenge for every form instance. A bound form that is
  re-rendered after a validation error shows a new challenge, because the
  submitted one may already be consumed.
- `clean()` verifies the submitted answer; raises `ValidationError` on
  wrong / expired / exhausted attempts.
- The widget produces `<img>` + hidden `captcha_id` + text input — render
  with `{{ form.captcha }}`.

## Customising the image URL

If your URL pattern isn't `/captcha/<id>.png`, pass the template:

```python
CaptchaField(manager=manager, image_url_pattern="/auth/challenge/{id}.png")
```

## Redis under WSGI

Under WSGI (gunicorn sync workers, `runserver`) there is no long-lived
event loop: every `async_to_sync` call creates a new loop and closes it
afterwards. A `redis.asyncio` connection belongs to the loop that opened
it, so a `RedisStorage` client shared by the module-level manager fails on
the **second** call:

```text
RuntimeError: Event loop is closed
```

Run the storage on one long-lived loop instead, and hand every call to it:

```python
import asyncio
import threading

from captchakit import Challenge, Storage


class LoopBridgedStorage:
    def __init__(self, inner: Storage) -> None:
        self.inner = inner
        self.loop = asyncio.new_event_loop()
        threading.Thread(target=self.loop.run_forever, daemon=True).start()

    async def _run(self, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        return await asyncio.wrap_future(future)

    async def put(self, challenge: Challenge) -> None:
        await self._run(self.inner.put(challenge))

    async def get(self, challenge_id: str) -> Challenge | None:
        return await self._run(self.inner.get(challenge_id))

    async def delete(self, challenge_id: str) -> None:
        await self._run(self.inner.delete(challenge_id))

    async def incr_attempts(self, challenge_id: str) -> int:
        return await self._run(self.inner.incr_attempts(challenge_id))


storage = LoopBridgedStorage(RedisStorage(client=Redis.from_url(REDIS_URL)))
```

The same applies to `RedisTokenBucket`. With a forking server, create the
loop lazily in each worker (after the fork). The
[captchakit-django-demo](https://github.com/akerem16/captchakit-django-demo/blob/main/captcha_demo/loop_bridge.py)
has a tested version that does this.

`MemoryStorage` is not affected. Neither are sync views under ASGI: there
`async_to_sync` hands the call to the server's single event loop.

## Async views

If your project already runs on ASGI, call the manager directly from
`async def` views (`await manager.verify(...)`). Do not call
`form.is_valid()` on a form with a `CaptchaField` inside an `async def`
view: `async_to_sync` raises `RuntimeError` in a thread that already runs
an event loop. Wrap it with `sync_to_async` instead.
