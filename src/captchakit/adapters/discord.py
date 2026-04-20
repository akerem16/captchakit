"""discord.py adapter.

Install with ``pip install "captchakit[discord]"``.

Exposes a single helper, :func:`send_captcha`, that issues a new challenge,
uploads the rendered PNG through ``channel.send`` as a file attachment, and
returns the challenge id. The caller persists that id (e.g. keyed by
``member.id`` in a dict, Redis, or a database) and calls
:meth:`CaptchaManager.verify` when the user replies.

Thin by design — the challenge lifecycle lives in
:class:`~captchakit.CaptchaManager`; state coordination with your bot's
cogs/commands is your concern.

Example::

    import discord
    from discord.ext import commands
    from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
    from captchakit.adapters.discord import send_captcha

    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    manager = CaptchaManager(
        MathChallengeFactory(), ImageRenderer(), MemoryStorage(),
    )
    pending: dict[int, str] = {}  # member_id -> challenge_id

    @bot.event
    async def on_member_join(member: discord.Member) -> None:
        dm = await member.create_dm()
        pending[member.id] = await send_captcha(dm, manager)

    @bot.event
    async def on_message(msg: discord.Message) -> None:
        cid = pending.get(msg.author.id)
        if cid is None or msg.guild is not None:
            return
        if await manager.verify(cid, msg.content):
            del pending[msg.author.id]
            await msg.channel.send("Welcome!")
"""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING

try:
    import discord
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "discord adapter requires the `discord` extra: pip install 'captchakit[discord]'"
    ) from exc

if TYPE_CHECKING:
    from discord.abc import Messageable

    from captchakit.manager import CaptchaManager


DEFAULT_CONTENT = "Please solve this captcha to continue."


async def send_captcha(
    channel: Messageable,
    manager: CaptchaManager,
    *,
    content: str = DEFAULT_CONTENT,
    filename: str = "captcha.png",
) -> str:
    """Issue a captcha, send it to ``channel``, return the challenge id.

    ``channel`` is anything implementing ``discord.abc.Messageable`` — a
    ``TextChannel``, ``DMChannel`` or ``Thread``. The rendered PNG is
    attached via :class:`discord.File`.
    """
    challenge_id, png_bytes = await manager.issue()
    await channel.send(
        content=content,
        file=discord.File(BytesIO(png_bytes), filename=filename),
    )
    return challenge_id


__all__ = ["send_captcha"]
