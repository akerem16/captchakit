from __future__ import annotations

import pytest

from captchakit import ChallengeSpec, EmojiGridChallengeFactory


class TestEmojiGrid:
    async def test_prompt_lists_every_cell(self) -> None:
        f = EmojiGridChallengeFactory(size=9)
        spec = await f.create()
        assert isinstance(spec, ChallengeSpec)
        # Every 1..size should appear in the prompt as "N."
        for n in range(1, 10):
            assert f"{n}." in spec.prompt

    async def test_solution_is_a_valid_position(self) -> None:
        f = EmojiGridChallengeFactory(size=9)
        for _ in range(25):
            spec = await f.create()
            assert spec.solution.isdigit()
            pos = int(spec.solution)
            assert 1 <= pos <= 9

    async def test_target_appears_at_solution_cell(self) -> None:
        f = EmojiGridChallengeFactory(size=9)
        for _ in range(25):
            spec = await f.create()
            # Prompt looks like: "Which cell contains 🍎? Reply with the number. 1.🍌 2.🍇 ..."
            _, _, tail = spec.prompt.partition("number.")
            cells = tail.strip().split(" ")
            # each cell is "N.emoji"
            pos = int(spec.solution)
            assert cells[pos - 1].startswith(f"{pos}.")
            # the cell at position contains exactly the target
            target = spec.prompt.split("contains ")[1].split("?")[0]
            assert cells[pos - 1] == f"{pos}.{target}"

    async def test_custom_pool(self) -> None:
        f = EmojiGridChallengeFactory(size=4, emoji_pool=("A", "B"))
        spec = await f.create()
        # every cell should be A or B
        tail = spec.prompt.split("number.")[1].strip().split(" ")
        for cell in tail:
            _, _, emoji = cell.partition(".")
            assert emoji in {"A", "B"}

    def test_rejects_small_size(self) -> None:
        with pytest.raises(ValueError):
            EmojiGridChallengeFactory(size=1)

    def test_rejects_pool_with_fewer_than_two_distinct(self) -> None:
        with pytest.raises(ValueError):
            EmojiGridChallengeFactory(emoji_pool=("🍎",))
        with pytest.raises(ValueError):
            EmojiGridChallengeFactory(emoji_pool=("🍎", "🍎"))
