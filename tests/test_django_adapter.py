from __future__ import annotations

import pytest

django = pytest.importorskip("django")


def _configure_django() -> None:
    from django.conf import settings  # noqa: PLC0415

    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={},
            INSTALLED_APPS=["django.contrib.contenttypes", "django.contrib.auth"],
            USE_TZ=True,
            SECRET_KEY="test",
        )
        django.setup()


_configure_django()

from captchakit import (  # noqa: E402
    CaptchaManager,
    ImageRenderer,
    MemoryStorage,
    TextChallengeFactory,
)
from captchakit.adapters.django import (  # noqa: E402
    CaptchaField,
    captcha_image_view,
)


@pytest.fixture
def manager() -> CaptchaManager:
    return CaptchaManager(
        factory=TextChallengeFactory(length=4),
        renderer=ImageRenderer(width=100, height=40, font_size=18),
        storage=MemoryStorage(),
        ttl=60.0,
    )


def test_captcha_field_issues_challenge_on_construct(manager: CaptchaManager) -> None:
    from django import forms  # noqa: PLC0415

    class MyForm(forms.Form):  # type: ignore[misc]
        captcha = CaptchaField(manager=manager)

    form = MyForm()
    cid, _ = form.fields["captcha"].initial
    assert isinstance(cid, str) and len(cid) == 32


def test_captcha_field_accepts_correct_answer(manager: CaptchaManager) -> None:
    from asgiref.sync import async_to_sync  # noqa: PLC0415
    from django import forms  # noqa: PLC0415

    class MyForm(forms.Form):  # type: ignore[misc]
        captcha = CaptchaField(manager=manager)

    form = MyForm()
    cid = form.fields["captcha"].initial[0]
    challenge = async_to_sync(manager.storage.get)(cid)
    assert challenge is not None

    posted = MyForm(
        data={"captcha_0": cid, "captcha_1": challenge.solution},
    )
    assert posted.is_valid(), posted.errors


def test_captcha_field_rejects_wrong_answer(manager: CaptchaManager) -> None:
    from django import forms  # noqa: PLC0415

    class MyForm(forms.Form):  # type: ignore[misc]
        captcha = CaptchaField(manager=manager)

    form = MyForm()
    cid = form.fields["captcha"].initial[0]

    posted = MyForm(data={"captcha_0": cid, "captcha_1": "definitely-wrong"})
    assert not posted.is_valid()


def test_form_instances_get_distinct_challenges(manager: CaptchaManager) -> None:
    # Regression: Django deep-copies class-level fields into every form
    # instance, so a challenge issued in CaptchaField.__init__ was shared by
    # all instances of the same form class.
    from asgiref.sync import async_to_sync  # noqa: PLC0415
    from django import forms  # noqa: PLC0415

    class MyForm(forms.Form):  # type: ignore[misc]
        captcha = CaptchaField(manager=manager)

    first = MyForm()
    second = MyForm()
    first_cid = first.fields["captcha"].initial[0]
    second_cid = second.fields["captcha"].initial[0]
    assert first_cid != second_cid

    first_challenge = async_to_sync(manager.storage.get)(first_cid)
    assert first_challenge is not None
    first_posted = MyForm(data={"captcha_0": first_cid, "captcha_1": first_challenge.solution})
    assert first_posted.is_valid(), first_posted.errors

    second_challenge = async_to_sync(manager.storage.get)(second_cid)
    assert second_challenge is not None
    posted = MyForm(data={"captcha_0": second_cid, "captcha_1": second_challenge.solution})
    assert posted.is_valid(), posted.errors


def test_captcha_field_rejects_empty_answer(manager: CaptchaManager) -> None:
    from django import forms  # noqa: PLC0415

    class MyForm(forms.Form):  # type: ignore[misc]
        captcha = CaptchaField(manager=manager)

    cid = MyForm().fields["captcha"].initial[0]
    posted = MyForm(data={"captcha_0": cid, "captcha_1": ""})
    assert not posted.is_valid()
    assert posted.errors["captcha"] == ["captcha is required"]
    assert CaptchaField(manager=manager).compress([]) == ("", "")


def test_captcha_field_rejects_consumed_challenge(manager: CaptchaManager) -> None:
    from asgiref.sync import async_to_sync  # noqa: PLC0415
    from django import forms  # noqa: PLC0415

    class MyForm(forms.Form):  # type: ignore[misc]
        captcha = CaptchaField(manager=manager)

    cid = MyForm().fields["captcha"].initial[0]
    challenge = async_to_sync(manager.storage.get)(cid)
    assert challenge is not None
    data = {"captcha_0": cid, "captcha_1": challenge.solution}

    assert MyForm(data=data).is_valid()
    replayed = MyForm(data=data)
    assert not replayed.is_valid()
    assert "captcha" in replayed.errors


def test_rerendered_bound_form_shows_fresh_challenge(manager: CaptchaManager) -> None:
    # A correct captcha is consumed even when another field fails, so the
    # re-rendered form must not echo the submitted id or answer.
    from asgiref.sync import async_to_sync  # noqa: PLC0415
    from django import forms  # noqa: PLC0415

    class MyForm(forms.Form):  # type: ignore[misc]
        username = forms.CharField()
        captcha = CaptchaField(manager=manager)

    cid = MyForm().fields["captcha"].initial[0]
    challenge = async_to_sync(manager.storage.get)(cid)
    assert challenge is not None

    posted = MyForm(data={"captcha_0": cid, "captcha_1": challenge.solution})
    assert not posted.is_valid()
    assert "username" in posted.errors
    assert "captcha" not in posted.errors

    new_cid, answer = posted["captcha"].value()
    assert new_cid != cid
    assert answer == ""
    assert async_to_sync(manager.storage.get)(new_cid) is not None
    assert f'value="{new_cid}"' in str(posted["captcha"])


def test_dynamically_added_field_issues_challenge(manager: CaptchaManager) -> None:
    from django import forms  # noqa: PLC0415

    form = forms.Form()
    form.fields["captcha"] = CaptchaField(manager=manager)
    cid, answer = form["captcha"].value()
    assert isinstance(cid, str) and len(cid) == 32
    assert answer == ""


def test_captcha_image_view_streams_bytes(manager: CaptchaManager) -> None:
    from asgiref.sync import async_to_sync  # noqa: PLC0415
    from django.http import Http404, HttpRequest  # noqa: PLC0415

    view = captcha_image_view(manager)
    cid, _ = async_to_sync(manager.issue)()

    request = HttpRequest()
    response = view(request, cid)
    assert response.status_code == 200
    assert response["Content-Type"].startswith("image/")
    assert len(response.content) > 0

    with pytest.raises(Http404):
        view(request, "nonexistent-id")
