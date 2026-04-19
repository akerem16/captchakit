"""Challenge types and factories."""

from __future__ import annotations

from pycaptcha.challenges.base import Challenge, ChallengeFactory, ChallengeSpec
from pycaptcha.challenges.math import MathChallengeFactory
from pycaptcha.challenges.text import TextChallengeFactory

__all__ = [
    "Challenge",
    "ChallengeFactory",
    "ChallengeSpec",
    "MathChallengeFactory",
    "TextChallengeFactory",
]
