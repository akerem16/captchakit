# aiogram adapter

Install: `pip install "captchakit[aiogram]"`.

The adapter exposes a single thin helper — `send_captcha` — which issues
a challenge, uploads the rendered PNG to Telegram via `bot.send_photo`,
and returns the challenge id. State management (pairing the id with the
user's eventual reply) belongs to your FSM.

## Helper

```python
from captchakit.adapters.aiogram import send_captcha

challenge_id = await send_captcha(
    bot,
    chat_id=user_id,
    manager=manager,
    caption="Solve this to join:",   # optional
    filename="captcha.png",          # optional
)
```

## End-to-end: chat-join verification

```python
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
```
