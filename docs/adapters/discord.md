# Discord adapter

Install: `pip install "captchakit[discord]"`.

Thin helper — `send_captcha` — issues a challenge, uploads the PNG as a
`discord.File` attachment, and returns the challenge id. Coordinating that
id with the user's later reply is your bot's job (a plain dict keyed by
`member.id` works fine; use Redis once you scale to multiple processes).

## Helper

```python
from captchakit.adapters.discord import send_captcha

challenge_id = await send_captcha(
    channel,               # anything Messageable: DMChannel, TextChannel, Thread
    manager,
    content="Prove you're human:",  # optional
    filename="captcha.png",         # optional
)
```

## End-to-end: on-join DM verification

```python
import discord
from discord.ext import commands
from captchakit import CaptchaManager, ImageRenderer, MathChallengeFactory, MemoryStorage
from captchakit.adapters.discord import send_captcha

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
manager = CaptchaManager(
    MathChallengeFactory(), ImageRenderer(), MemoryStorage(),
)
pending: dict[int, str] = {}

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
```
