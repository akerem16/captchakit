from __future__ import annotations

import pytest

from captchakit import (
    CaptchaKitError,
    ChallengeError,
    ChallengeExpired,
    ChallengeNotFound,
    StorageError,
    TooManyAttempts,
)


@pytest.mark.parametrize(
    "cls",
    [ChallengeNotFound, ChallengeExpired, TooManyAttempts],
)
def test_challenge_id_attached(cls: type[ChallengeError]) -> None:
    exc = cls("abc")
    assert isinstance(exc, CaptchaKitError)
    assert exc.challenge_id == "abc"
    assert "abc" in str(exc)


def test_storage_error_is_base() -> None:
    assert issubclass(StorageError, CaptchaKitError)
