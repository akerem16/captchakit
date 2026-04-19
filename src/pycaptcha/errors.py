"""Exception hierarchy for pycaptcha."""

from __future__ import annotations


class PyCaptchaError(Exception):
    """Base class for all pycaptcha exceptions."""


class ChallengeError(PyCaptchaError):
    """Base for errors that reference a specific challenge id.

    Catch this to handle :class:`ChallengeNotFound`, :class:`ChallengeExpired`
    and :class:`TooManyAttempts` uniformly.
    """

    _template: str = "challenge error: {id!r}"

    def __init__(self, challenge_id: str) -> None:
        super().__init__(self._template.format(id=challenge_id))
        self.challenge_id: str = challenge_id


class ChallengeNotFound(ChallengeError):
    """The referenced challenge id does not exist in storage."""

    _template = "challenge not found: {id!r}"


class ChallengeExpired(ChallengeError):
    """The challenge has passed its expiration time."""

    _template = "challenge expired: {id!r}"


class TooManyAttempts(ChallengeError):
    """The allowed number of verification attempts has been exceeded."""

    _template = "too many attempts for challenge: {id!r}"


class StorageError(PyCaptchaError):
    """Underlying storage backend failed."""
