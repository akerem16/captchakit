"""Core challenge protocol and dataclasses."""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True, slots=True)
class ChallengeSpec:
    """A challenge's raw content before an id/TTL is attached.

    Produced by a :class:`ChallengeFactory`; the :class:`~captchakit.CaptchaManager`
    wraps it into a :class:`Challenge` with identifier and timestamps.
    """

    prompt: str
    solution: str
    case_sensitive: bool = False


@dataclass(frozen=True, slots=True)
class Challenge:
    """A complete captcha challenge stored by the manager."""

    id: str
    prompt: str
    solution: str
    created_at: float
    expires_at: float
    case_sensitive: bool = False

    def is_expired(self, now: float) -> bool:
        return now > self.expires_at

    def check(self, user_input: str) -> bool:
        """Constant-time comparison against the expected solution."""
        expected = self.solution
        got = user_input.strip()
        if not self.case_sensitive:
            expected = expected.casefold()
            got = got.casefold()
        return hmac.compare_digest(expected.encode("utf-8"), got.encode("utf-8"))


@runtime_checkable
class ChallengeFactory(Protocol):
    """Produces fresh :class:`ChallengeSpec` instances on demand."""

    async def create(self) -> ChallengeSpec:  # pragma: no cover - protocol
        ...
