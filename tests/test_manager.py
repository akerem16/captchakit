from __future__ import annotations

import pytest

from captchakit import (
    CaptchaManager,
    ChallengeExpired,
    ChallengeNotFound,
    ImageRenderer,
    MemoryStorage,
    TextChallengeFactory,
    TooManyAttempts,
)

from .conftest import FakeClock


async def test_issue_returns_id_and_png(text_manager: CaptchaManager) -> None:
    cid, png = await text_manager.issue()
    assert isinstance(cid, str) and len(cid) == 32
    assert png.startswith(b"\x89PNG")


async def test_verify_happy_path(text_manager: CaptchaManager, storage: MemoryStorage) -> None:
    cid, _ = await text_manager.issue()
    ch = await storage.get(cid)
    assert ch is not None
    assert await text_manager.verify(cid, ch.solution) is True
    # challenge consumed after success
    assert await storage.get(cid) is None


async def test_verify_wrong_answer_returns_false(
    text_manager: CaptchaManager, storage: MemoryStorage
) -> None:
    cid, _ = await text_manager.issue()
    assert await text_manager.verify(cid, "definitely-not-right") is False
    # challenge still alive while attempts remain
    assert await storage.get(cid) is not None


async def test_verify_missing_raises(text_manager: CaptchaManager) -> None:
    with pytest.raises(ChallengeNotFound):
        await text_manager.verify("nonexistent", "x")


async def test_verify_expired_raises_and_evicts(
    text_manager: CaptchaManager, clock: FakeClock, storage: MemoryStorage
) -> None:
    cid, _ = await text_manager.issue()
    clock.advance(text_manager.ttl + 1.0)
    with pytest.raises(ChallengeExpired):
        await text_manager.verify(cid, "anything")
    assert await storage.get(cid) is None


async def test_verify_too_many_attempts(
    text_manager: CaptchaManager, storage: MemoryStorage
) -> None:
    cid, _ = await text_manager.issue()
    for _ in range(text_manager.max_attempts - 1):
        assert await text_manager.verify(cid, "wrong") is False
    with pytest.raises(TooManyAttempts):
        await text_manager.verify(cid, "still-wrong")
    assert await storage.get(cid) is None


async def test_discard_removes(text_manager: CaptchaManager, storage: MemoryStorage) -> None:
    cid, _ = await text_manager.issue()
    await text_manager.discard(cid)
    assert await storage.get(cid) is None


def test_manager_rejects_bad_config() -> None:
    with pytest.raises(ValueError):
        CaptchaManager(
            factory=TextChallengeFactory(),
            renderer=ImageRenderer(),
            storage=MemoryStorage(),
            ttl=0,
        )
    with pytest.raises(ValueError):
        CaptchaManager(
            factory=TextChallengeFactory(),
            renderer=ImageRenderer(),
            storage=MemoryStorage(),
            max_attempts=0,
        )
