"""Wordlist-based challenges.

An accessibility-oriented alternative to :class:`TextChallengeFactory`:
the user reads a real word from the image instead of a random letter
scramble, which is easier for people using screen magnifiers or dealing
with dyslexia, while still providing a reasonable bot-deterrent.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field

from captchakit.challenges.base import ChallengeSpec

# A small bundled wordlist of common, unambiguous 5-letter English words.
# Deliberately avoids offensive / politically charged terms.
DEFAULT_WORDS: tuple[str, ...] = (
    "apple", "brave", "chair", "dream", "eagle",
    "flame", "grape", "happy", "ivory", "jolly",
    "knife", "lemon", "maple", "night", "olive",
    "piano", "quilt", "river", "smile", "table",
    "umbra", "voice", "wheat", "young", "zebra",
    "bread", "cloud", "dance", "earth", "field",
    "glory", "honey", "inbox", "jumbo", "karma",
    "light", "music", "novel", "ocean", "paint",
    "quick", "raven", "storm", "tiger", "urban",
    "vivid", "waltz", "xenon", "yacht", "zesty",
)  # fmt: skip


@dataclass(slots=True)
class WordChallengeFactory:
    """Produces a single random word from a wordlist.

    The default list avoids visually / phonetically ambiguous words and
    ships ~50 common English nouns. Pass your own ``words`` tuple to
    localise or narrow the pool.
    """

    words: tuple[str, ...] = field(default_factory=lambda: DEFAULT_WORDS)
    case_sensitive: bool = False

    def __post_init__(self) -> None:
        if not self.words:
            raise ValueError("words must be non-empty")
        if any(not w.strip() for w in self.words):
            raise ValueError("words must not contain empty strings")

    async def create(self) -> ChallengeSpec:
        word = secrets.choice(self.words)
        return ChallengeSpec(
            prompt=word,
            solution=word,
            case_sensitive=self.case_sensitive,
        )
