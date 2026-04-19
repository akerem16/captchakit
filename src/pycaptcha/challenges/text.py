"""Alphanumeric text challenges."""

from __future__ import annotations

import secrets
from dataclasses import dataclass

from pycaptcha.challenges.base import ChallengeSpec

DEFAULT_CHARSET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


@dataclass(slots=True)
class TextChallengeFactory:
    """Produces random alphanumeric strings.

    The default charset omits visually ambiguous characters
    (``I``, ``O``, ``0``, ``1``) so a user isn't penalised for font choice.
    """

    length: int = 5
    charset: str = DEFAULT_CHARSET
    case_sensitive: bool = False

    def __post_init__(self) -> None:
        if self.length < 1:
            raise ValueError("length must be >= 1")
        if not self.charset:
            raise ValueError("charset must be non-empty")

    async def create(self) -> ChallengeSpec:
        solution = "".join(secrets.choice(self.charset) for _ in range(self.length))
        return ChallengeSpec(
            prompt=solution,
            solution=solution,
            case_sensitive=self.case_sensitive,
        )
