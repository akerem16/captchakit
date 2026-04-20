"""aiogram (Telegram bot framework) adapter.

Install with ``pip install "captchakit[aiogram]"``.

Exposes a single helper, :func:`send_captcha`, that issues a new challenge,
uploads the rendered image to Telegram as a photo, and returns the
challenge id. The caller persists that id (typically via aiogram's FSM) and
calls :meth:`CaptchaManager.verify` on the user's reply.

This stays intentionally thin — challenge lifecycle belongs to
:class:`~captchakit.CaptchaManager`, and user/session state belongs to
whatever storage aiogram's FSM is already using.

Example::

    from aiogram import F
    from aiogram.fsm.context import FSMContext
    from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
    from captchakit.adapters.aiogram import send_captcha

    manager = CaptchaManager(
        MathChallengeFactory(), ImageRenderer(), MemoryStorage(),
    )

    @dp.chat_join_request()
    async def on_join(req, state: FSMContext):
        cid = await send_captcha(req.bot, req.from_user.id, manager)
        await state.update_data(captcha_id=cid, join_chat_id=req.chat.id)

    @dp.message(F.text)
    async def on_reply(msg, state: FSMContext):
        data = await state.get_data()
        cid = data.get("captcha_id")
        if cid is None:
            return
        if await manager.verify(cid, msg.text):
            await msg.bot.approve_chat_join_request(
                data["join_chat_id"], msg.from_user.id,
            )
            await state.clear()
"""

from __future__ import annotations

from typing import TYPE_CHECKING

try:
    from aiogram.types import BufferedInputFile
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "aiogram adapter requires the `aiogram` extra: pip install 'captchakit[aiogram]'"
    ) from exc

if TYPE_CHECKING:
    from aiogram import Bot

    from captchakit.manager import CaptchaManager


DEFAULT_CAPTION = "Please solve this captcha to continue."


async def send_captcha(
    bot: Bot,
    chat_id: int,
    manager: CaptchaManager,
    *,
    caption: str = DEFAULT_CAPTION,
    filename: str = "captcha.png",
) -> str:
    """Issue a captcha, send the image to ``chat_id``, return the challenge id.

    The caller is responsible for persisting the returned id (typically in
    aiogram's FSM) and for calling :meth:`CaptchaManager.verify` when the
    user replies.
    """
    challenge_id, png_bytes = await manager.issue()
    await bot.send_photo(
        chat_id=chat_id,
        photo=BufferedInputFile(png_bytes, filename=filename),
        caption=caption,
    )
    return challenge_id


__all__ = ["send_captcha"]
