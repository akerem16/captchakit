"""captchakit — async-first, typed captcha library."""

from __future__ import annotations

from captchakit._clock import Clock, MonotonicClock
from captchakit.challenges import (
    Challenge,
    ChallengeFactory,
    ChallengeSpec,
    EmojiGridChallengeFactory,
    MathChallengeFactory,
    TextChallengeFactory,
)
from captchakit.errors import (
    CaptchaKitError,
    ChallengeError,
    ChallengeExpired,
    ChallengeNotFound,
    StorageError,
    TooManyAttempts,
)
from captchakit.manager import CaptchaManager
from captchakit.renderers import ImageRenderer, Renderer
from captchakit.storage import MemoryStorage, Storage

__version__ = "0.2.0"

__all__ = [
    "CaptchaKitError",
    "CaptchaManager",
    "Challenge",
    "ChallengeError",
    "ChallengeExpired",
    "ChallengeFactory",
    "ChallengeNotFound",
    "ChallengeSpec",
    "Clock",
    "EmojiGridChallengeFactory",
    "ImageRenderer",
    "MathChallengeFactory",
    "MemoryStorage",
    "MonotonicClock",
    "Renderer",
    "Storage",
    "StorageError",
    "TextChallengeFactory",
    "TooManyAttempts",
    "__version__",
]
