# Audio challenges

`AudioRenderer` is the accessibility alternative to `ImageRenderer`. It
encodes the challenge's solution as a sequence of sine-wave tones — one
per character — and returns a WAV byte-stream. No extra dependencies.

```python
from captchakit import (
    AudioRenderer,
    CaptchaManager,
    MemoryStorage,
    TextChallengeFactory,
)

manager = CaptchaManager(
    factory=TextChallengeFactory(length=5, charset="0123456789"),
    renderer=AudioRenderer(),
    storage=MemoryStorage(),
)
cid, wav_bytes = await manager.issue()
```

Each character is mapped to a frequency (digits climb a pentatonic
scale; lowercase letters span 300–1200 Hz). The result is **not**
intelligible speech — it is a distinctive, bot-unfriendly audio
fingerprint that a human with audio can transcribe after one or two
listens.

## Pairing with image renderer

Best practice for accessibility: expose both renderers and let the user
pick. Hold on to the challenge id across the two endpoints:

```python
# single manager, dispatch rendering in the adapter layer
spec = await manager.factory.create()
...
# OR use two managers sharing a Storage
```

For a quick approach, issue with the image renderer and render a second
WAV on demand using the stored `Challenge.solution`.

## Custom tone mapping

```python
from captchakit import AudioRenderer

renderer = AudioRenderer(
    tone_map={"0": 300.0, "1": 400.0, "2": 500.0},
    fallback_freq=220.0,
    tone_ms=500,
    gap_ms=150,
)
```

## Beyond tones: real TTS

If you need a human voice saying the characters, write a small adapter
around `gTTS`, `pyttsx3` or a cloud TTS API — anything that implements
the `Renderer` protocol (`async def render(challenge) -> bytes` +
`content_type`) works. captchakit intentionally keeps TTS out of the
core to avoid heavy runtime dependencies.
