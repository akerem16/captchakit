"""Emoji-grid challenges.

A simple single-pick variant: one target emoji is placed in a random cell
of a grid populated with distractor emojis. The user types the 1-indexed
position number. Useful for Telegram / Discord inline-button flows where
each cell becomes a button.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field

from captchakit.challenges.base import ChallengeSpec
from captchakit.i18n import PromptTranslator

DEFAULT_EMOJI_POOL: tuple[str, ...] = (
    "🍎",
    "🍌",
    "🍇",
    "🍓",
    "🍊",
    "🍉",
    "🍒",
    "🍑",
    "🥝",
    "🍍",
    "🥥",
    "🍋",
)


@dataclass(slots=True)
class EmojiGridChallengeFactory:
    """Produces a single-pick emoji-grid challenge.

    One target emoji is placed in a randomly chosen cell; the remaining
    cells are filled with distractors drawn from ``emoji_pool``. The user's
    expected answer is the 1-indexed cell number as a string (e.g. ``"3"``).
    """

    size: int = 9
    emoji_pool: tuple[str, ...] = field(default_factory=lambda: DEFAULT_EMOJI_POOL)
    translator: PromptTranslator | None = None
    locale: str = "en"

    def __post_init__(self) -> None:
        min_count = 2
        if self.size < min_count:
            raise ValueError("size must be >= 2")
        if len(set(self.emoji_pool)) < min_count:
            raise ValueError("emoji_pool needs at least 2 distinct emojis")

    async def create(self) -> ChallengeSpec:
        target = secrets.choice(self.emoji_pool)
        position = secrets.randbelow(self.size)
        distractors = tuple(e for e in self.emoji_pool if e != target)
        grid = [target if i == position else secrets.choice(distractors) for i in range(self.size)]
        numbered = " ".join(f"{i + 1}.{emoji}" for i, emoji in enumerate(grid))
        if self.translator is not None:
            head = self.translator.translate("grid.pick", self.locale, emoji=target)
        else:
            head = f"Which cell contains {target}? Reply with the number."
        prompt = f"{head} {numbered}"
        return ChallengeSpec(
            prompt=prompt,
            solution=str(position + 1),
            case_sensitive=False,
        )
