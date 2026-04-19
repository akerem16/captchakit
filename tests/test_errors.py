from __future__ import annotations

import pytest

from pycaptcha import (
    ChallengeError,
    ChallengeExpired,
    ChallengeNotFound,
    PyCaptchaError,
    StorageError,
    TooManyAttempts,
)


@pytest.mark.parametrize(
    "cls",
    [ChallengeNotFound, ChallengeExpired, TooManyAttempts],
)
def test_challenge_id_attached(cls: type[ChallengeError]) -> None:
    exc = cls("abc")
    assert isinstance(exc, PyCaptchaError)
    assert exc.challenge_id == "abc"
    assert "abc" in str(exc)


def test_storage_error_is_base() -> None:
    assert issubclass(StorageError, PyCaptchaError)
