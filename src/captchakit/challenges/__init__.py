"""Challenge types and factories."""

from __future__ import annotations

from captchakit.challenges.base import Challenge, ChallengeFactory, ChallengeSpec
from captchakit.challenges.grid import EmojiGridChallengeFactory
from captchakit.challenges.math import MathChallengeFactory
from captchakit.challenges.text import TextChallengeFactory

__all__ = [
    "Challenge",
    "ChallengeFactory",
    "ChallengeSpec",
    "EmojiGridChallengeFactory",
    "MathChallengeFactory",
    "TextChallengeFactory",
]
