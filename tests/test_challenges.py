from __future__ import annotations

import pytest

from pycaptcha import (
    Challenge,
    ChallengeSpec,
    MathChallengeFactory,
    TextChallengeFactory,
)
from pycaptcha.challenges.text import DEFAULT_CHARSET


def _make(solution: str, *, case_sensitive: bool = False) -> Challenge:
    return Challenge(
        id="x",
        prompt=solution,
        solution=solution,
        created_at=0.0,
        expires_at=1000.0,
        case_sensitive=case_sensitive,
    )


def test_challenge_check_strips_and_casefolds() -> None:
    ch = _make("Abc23")
    assert ch.check(" abc23 ")
    assert ch.check("ABC23")
    assert not ch.check("abc24")


def test_challenge_check_case_sensitive() -> None:
    ch = _make("Abc23", case_sensitive=True)
    assert ch.check("Abc23")
    assert not ch.check("abc23")


def test_challenge_is_expired() -> None:
    ch = _make("x")
    assert not ch.is_expired(999.0)
    assert ch.is_expired(1001.0)


class TestTextFactory:
    async def test_length_and_charset(self) -> None:
        f = TextChallengeFactory(length=8)
        spec = await f.create()
        assert isinstance(spec, ChallengeSpec)
        assert len(spec.solution) == 8
        assert all(c in DEFAULT_CHARSET for c in spec.solution)
        assert spec.prompt == spec.solution

    async def test_custom_charset(self) -> None:
        f = TextChallengeFactory(length=10, charset="ab")
        spec = await f.create()
        assert set(spec.solution).issubset({"a", "b"})

    def test_rejects_non_positive_length(self) -> None:
        with pytest.raises(ValueError):
            TextChallengeFactory(length=0)

    def test_rejects_empty_charset(self) -> None:
        with pytest.raises(ValueError):
            TextChallengeFactory(charset="")


class TestMathFactory:
    async def test_addition_result_matches(self) -> None:
        f = MathChallengeFactory(min_operand=1, max_operand=9, operators=("+",))
        for _ in range(25):
            spec = await f.create()
            a, _, b = spec.prompt.replace(" = ?", "").split(" ")
            assert int(spec.solution) == int(a) + int(b)

    async def test_subtraction_non_negative(self) -> None:
        f = MathChallengeFactory(operators=("-",))
        for _ in range(25):
            spec = await f.create()
            assert int(spec.solution) >= 0

    async def test_multiplication(self) -> None:
        f = MathChallengeFactory(operators=("*",))
        spec = await f.create()
        a, _, b = spec.prompt.replace(" = ?", "").split(" ")
        assert int(spec.solution) == int(a) * int(b)

    def test_validation(self) -> None:
        with pytest.raises(ValueError):
            MathChallengeFactory(min_operand=-1)
        with pytest.raises(ValueError):
            MathChallengeFactory(min_operand=5, max_operand=2)
        with pytest.raises(ValueError):
            MathChallengeFactory(operators=())
