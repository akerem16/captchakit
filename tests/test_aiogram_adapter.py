from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

pytest.importorskip("aiogram")

from captchakit import (
    CaptchaManager,
    ImageRenderer,
    MathChallengeFactory,
    MemoryStorage,
    TextChallengeFactory,
)
from captchakit.adapters.aiogram import DEFAULT_CAPTION, send_captcha


def _make_manager(factory_kind: str = "text") -> CaptchaManager:
    factory = TextChallengeFactory(length=4) if factory_kind == "text" else MathChallengeFactory()
    return CaptchaManager(
        factory=factory,
        renderer=ImageRenderer(width=120, height=60, font_size=24),
        storage=MemoryStorage(),
        ttl=60.0,
    )


async def test_send_captcha_calls_bot_send_photo_and_returns_id() -> None:
    bot = AsyncMock()
    manager = _make_manager()
    cid = await send_captcha(bot, chat_id=42, manager=manager)

    assert isinstance(cid, str) and len(cid) == 32
    bot.send_photo.assert_awaited_once()
    kwargs: dict[str, Any] = bot.send_photo.call_args.kwargs
    assert kwargs["chat_id"] == 42
    assert kwargs["caption"] == DEFAULT_CAPTION
    # BufferedInputFile wraps the PNG bytes
    photo = kwargs["photo"]
    assert photo.filename == "captcha.png"
    # aiogram's BufferedInputFile stores the bytes on `.data`
    assert photo.data.startswith(b"\x89PNG")


async def test_send_captcha_custom_caption_and_filename() -> None:
    bot = AsyncMock()
    manager = _make_manager(factory_kind="math")
    cid = await send_captcha(
        bot,
        chat_id=7,
        manager=manager,
        caption="Solve this:",
        filename="puzzle.png",
    )
    assert cid
    kwargs = bot.send_photo.call_args.kwargs
    assert kwargs["caption"] == "Solve this:"
    assert kwargs["photo"].filename == "puzzle.png"


async def test_challenge_is_stored_and_verifiable() -> None:
    bot = AsyncMock()
    manager = _make_manager()
    cid = await send_captcha(bot, chat_id=1, manager=manager)

    ch = await manager.storage.get(cid)
    assert ch is not None
    assert await manager.verify(cid, ch.solution) is True
