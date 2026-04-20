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

- Issues a fresh challenge on unbound form construction.
- `clean()` verifies the submitted answer; raises `ValidationError` on
  wrong / expired / exhausted attempts.
- The widget produces `<img>` + hidden `captcha_id` + text input — render
  with `{{ form.captcha }}`.

## Customising the image URL

If your URL pattern isn't `/captcha/<id>.png`, pass the template:

```python
CaptchaField(manager=manager, image_url_pattern="/auth/challenge/{id}.png")
```

## Async views

If your project already runs on ASGI, you can skip the sync bridge and
call the manager directly from async views. The form field still works —
`async_to_sync` is safe inside an ASGI loop.
