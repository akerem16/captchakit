from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock

import pytest

pytest.importorskip("discord")

from captchakit import (
    CaptchaManager,
    ImageRenderer,
    MathChallengeFactory,
    MemoryStorage,
    TextChallengeFactory,
)
from captchakit.adapters.discord import DEFAULT_CONTENT, send_captcha


def _make_manager(factory_kind: str = "text") -> CaptchaManager:
    factory = TextChallengeFactory(length=4) if factory_kind == "text" else MathChallengeFactory()
    return CaptchaManager(
        factory=factory,
        renderer=ImageRenderer(width=120, height=60, font_size=24),
        storage=MemoryStorage(),
        ttl=60.0,
    )


async def test_send_captcha_calls_channel_send_and_returns_id() -> None:
    channel = AsyncMock()
    manager = _make_manager()
    cid = await send_captcha(channel, manager)

    assert isinstance(cid, str) and len(cid) == 32
    channel.send.assert_awaited_once()
    kwargs: dict[str, Any] = channel.send.call_args.kwargs
    assert kwargs["content"] == DEFAULT_CONTENT
    file = kwargs["file"]
    assert file.filename == "captcha.png"


async def test_send_captcha_custom_content_and_filename() -> None:
    channel = AsyncMock()
    manager = _make_manager(factory_kind="math")
    cid = await send_captcha(
        channel,
        manager,
        content="Prove you're human:",
        filename="puzzle.png",
    )
    assert cid
    kwargs = channel.send.call_args.kwargs
    assert kwargs["content"] == "Prove you're human:"
    assert kwargs["file"].filename == "puzzle.png"


async def test_challenge_stored_and_verifiable() -> None:
    channel = AsyncMock()
    manager = _make_manager()
    cid = await send_captcha(channel, manager)

    ch = await manager.storage.get(cid)
    assert ch is not None
    assert await manager.verify(cid, ch.solution) is True
