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
    WordChallengeFactory,
)
from captchakit.errors import (
    CaptchaKitError,
    ChallengeError,
    ChallengeExpired,
    ChallengeNotFound,
    RateLimited,
    StorageError,
    TooManyAttempts,
)
from captchakit.i18n import DefaultTranslator, PromptTranslator
from captchakit.manager import CaptchaManager
from captchakit.metrics import MetricsSink, NoOpMetrics
from captchakit.ratelimit import NoOpRateLimiter, RateLimiter, TokenBucketRateLimiter
from captchakit.renderers import AudioRenderer, ImageRenderer, Renderer, SVGRenderer, Theme
from captchakit.storage import MemoryStorage, Storage

__version__ = "1.0.1"

__all__ = [
    "AudioRenderer",
    "CaptchaKitError",
    "CaptchaManager",
    "Challenge",
    "ChallengeError",
    "ChallengeExpired",
    "ChallengeFactory",
    "ChallengeNotFound",
    "ChallengeSpec",
    "Clock",
    "DefaultTranslator",
    "EmojiGridChallengeFactory",
    "ImageRenderer",
    "MathChallengeFactory",
    "MemoryStorage",
    "MetricsSink",
    "MonotonicClock",
    "NoOpMetrics",
    "NoOpRateLimiter",
    "PromptTranslator",
    "RateLimited",
    "RateLimiter",
    "Renderer",
    "SVGRenderer",
    "Storage",
    "StorageError",
    "TextChallengeFactory",
    "Theme",
    "TokenBucketRateLimiter",
    "TooManyAttempts",
    "WordChallengeFactory",
    "__version__",
]
