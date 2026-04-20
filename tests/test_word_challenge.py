from __future__ import annotations

import pytest

from captchakit import ChallengeSpec, WordChallengeFactory
from captchakit.challenges.word import DEFAULT_WORDS


class TestWordChallenge:
    async def test_output_is_from_pool(self) -> None:
        f = WordChallengeFactory()
        for _ in range(25):
            spec = await f.create()
            assert isinstance(spec, ChallengeSpec)
            assert spec.solution in DEFAULT_WORDS
            assert spec.prompt == spec.solution

    async def test_custom_pool(self) -> None:
        f = WordChallengeFactory(words=("alpha", "beta"))
        seen: set[str] = set()
        for _ in range(25):
            spec = await f.create()
            seen.add(spec.solution)
        assert seen.issubset({"alpha", "beta"})

    async def test_case_sensitive_override(self) -> None:
        f = WordChallengeFactory(words=("Apple",), case_sensitive=True)
        spec = await f.create()
        assert spec.case_sensitive is True

    def test_rejects_empty_pool(self) -> None:
        with pytest.raises(ValueError):
            WordChallengeFactory(words=())

    def test_rejects_blank_words(self) -> None:
        with pytest.raises(ValueError):
            WordChallengeFactory(words=("apple", "   "))
