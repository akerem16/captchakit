"""Django adapter.

Install with ``pip install "captchakit[django]"``.

Django is sync-first, so the adapter bridges :class:`CaptchaManager`'s
async API via :func:`asgiref.sync.async_to_sync`.

Usage
-----

Wire a module-level manager (reuse the same instance across views)::

    # app/captcha.py
    from captchakit import CaptchaManager, ImageRenderer, MemoryStorage, TextChallengeFactory

    manager = CaptchaManager(
        factory=TextChallengeFactory(length=5),
        renderer=ImageRenderer(),
        storage=MemoryStorage(),
    )

Expose the image view in ``urls.py``::

    from captchakit.adapters.django import captcha_image_view
    from app.captcha import manager

    urlpatterns = [
        path("captcha/<str:challenge_id>.png", captcha_image_view(manager)),
    ]

Drop :class:`CaptchaField` into a form::

    from django import forms
    from captchakit.adapters.django import CaptchaField
    from app.captcha import manager

    class RegisterForm(forms.Form):
        username = forms.CharField()
        captcha = CaptchaField(manager=manager)

The field issues a fresh challenge on each GET and verifies the user's
answer on POST. Render it with ``{{ form.captcha }}`` — the widget
produces a hidden ``captcha_id`` input, an ``<img>`` tag pointing at
the image view, and a text input for the answer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

try:
    from asgiref.sync import async_to_sync
    from django import forms
    from django.core.exceptions import ValidationError
    from django.http import Http404, HttpRequest, HttpResponse
    from django.utils.safestring import mark_safe
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Django adapter requires the `django` extra: pip install 'captchakit[django]'"
    ) from exc

from captchakit.errors import ChallengeError

if TYPE_CHECKING:
    from collections.abc import Callable

    from captchakit.manager import CaptchaManager


class CaptchaWidget(forms.MultiWidget):  # type: ignore[misc]
    """Renders a hidden challenge id + image + answer input."""

    image_url_pattern: str = "/captcha/{id}.png"

    def __init__(self, image_url_pattern: str = "/captcha/{id}.png") -> None:
        self.image_url_pattern = image_url_pattern
        super().__init__(
            widgets=(forms.HiddenInput(), forms.TextInput()),
        )

    def decompress(self, value: Any) -> list[Any]:
        if value is None:
            return [None, None]
        return list(value)

    def render(
        self,
        name: str,
        value: Any,
        attrs: dict[str, Any] | None = None,
        renderer: Any = None,
    ) -> str:
        base = super().render(name, value, attrs, renderer)
        challenge_id = (value or [None, None])[0] or ""
        img = (
            f'<img src="{self.image_url_pattern.format(id=challenge_id)}" '
            f'alt="captcha" class="captcha-image">'
            if challenge_id
            else ""
        )
        result: str = mark_safe(img + base)  # noqa: S308
        return result


class CaptchaField(forms.MultiValueField):  # type: ignore[misc]
    """Form field that owns a captcha challenge end-to-end.

    Issues a fresh challenge when the form is built unbound, and
    verifies the submitted answer in :meth:`clean`. Construct with the
    :class:`CaptchaManager` to use.
    """

    widget = CaptchaWidget

    def __init__(
        self,
        manager: CaptchaManager,
        *,
        image_url_pattern: str = "/captcha/{id}.png",
        **kwargs: Any,
    ) -> None:
        self._manager = manager
        fields = (
            forms.CharField(widget=forms.HiddenInput()),
            forms.CharField(),
        )
        kwargs.setdefault("require_all_fields", True)
        super().__init__(
            fields=fields,
            widget=CaptchaWidget(image_url_pattern=image_url_pattern),
            **kwargs,
        )
        # Pre-issue a challenge so the widget has an id to render.
        self._refresh_challenge()

    def _refresh_challenge(self) -> None:
        cid, _ = async_to_sync(self._manager.issue)()
        self.initial = [cid, ""]

    def compress(self, data_list: list[Any]) -> tuple[str, str]:
        if not data_list or len(data_list) < 2:  # noqa: PLR2004
            return ("", "")
        return (data_list[0] or "", data_list[1] or "")

    def clean(self, value: Any) -> tuple[str, str]:
        cid, answer = self.compress(value) if isinstance(value, list) else (value or ("", ""))
        if not cid or not answer:
            raise ValidationError("captcha is required")
        try:
            ok = async_to_sync(self._manager.verify)(cid, answer)
        except ChallengeError as exc:
            raise ValidationError(str(exc)) from exc
        if not ok:
            raise ValidationError("wrong captcha answer")
        return (cid, answer)


def captcha_image_view(manager: CaptchaManager) -> Callable[[HttpRequest, str], HttpResponse]:
    """View function that streams the challenge image by id."""

    def _view(request: HttpRequest, challenge_id: str) -> HttpResponse:  # noqa: ARG001
        challenge = async_to_sync(manager.storage.get)(challenge_id)
        if challenge is None:
            raise Http404("captcha not found")
        image = async_to_sync(manager.renderer.render)(challenge)
        return HttpResponse(image, content_type=manager.renderer.content_type)

    return _view


__all__ = ["CaptchaField", "CaptchaWidget", "captcha_image_view"]
