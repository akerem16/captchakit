"""Audio renderer for accessibility.

Produces a WAV byte-stream that encodes the challenge's *solution* as a
sequence of sine-wave tones — one distinct frequency per character. It is
deliberately simple and dependency-free (stdlib :mod:`wave` + :mod:`math`);
the goal is an accessible alternative to :class:`ImageRenderer` for users
who cannot see the image.

If you need real text-to-speech (a human voice saying the characters), pass
a custom :class:`captchakit.renderers.base.Renderer` wired to gTTS, pyttsx3
or a cloud TTS API — this module does not pull in heavy deps.

The ``[audio]`` extra is reserved for future additions (``gTTS``, ``pydub``);
the built-in tone renderer itself needs nothing beyond the stdlib.
"""

from __future__ import annotations

import asyncio
import io
import math
import struct
import wave
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

_MIN_SAMPLE_RATE = 8000

if TYPE_CHECKING:
    from captchakit.challenges.base import Challenge


def _default_tone_map() -> dict[str, float]:
    """Digit + lowercase letter → frequency in Hz (roughly musical).

    Digits 0-9 climb a pentatonic scale; letters a-z span 300-1200 Hz.
    Anything not mapped uses a neutral 440 Hz beep.
    """

    mapping: dict[str, float] = {}
    digits = [261.6, 293.7, 329.6, 349.2, 392.0, 440.0, 493.9, 523.3, 587.3, 659.3]
    for i, freq in enumerate(digits):
        mapping[str(i)] = freq
    span = 1200 - 300
    for idx, ch in enumerate("abcdefghijklmnopqrstuvwxyz"):
        mapping[ch] = 300 + (span * idx / 25)
    return mapping


@dataclass(slots=True)
class AudioRenderer:
    """Renders a challenge's solution into a WAV byte-stream.

    Each character of the solution becomes ``tone_ms`` of a sine wave at
    the frequency mapped in ``tone_map``; tones are separated by
    ``gap_ms`` of silence. Output is mono 16-bit PCM at ``sample_rate``
    samples per second.

    The renderer is **not** meant to defeat bots — it is an
    accessibility alternative. Pair it with rate-limiting at the edge.
    """

    sample_rate: int = 16000
    tone_ms: int = 450
    gap_ms: int = 200
    amplitude: float = 0.35
    tone_map: dict[str, float] = field(default_factory=_default_tone_map)
    fallback_freq: float = 440.0
    content_type: str = "audio/wav"

    def __post_init__(self) -> None:
        if not 0 < self.amplitude <= 1:
            raise ValueError("amplitude must be in (0, 1]")
        if self.sample_rate < _MIN_SAMPLE_RATE:
            raise ValueError(f"sample_rate must be >= {_MIN_SAMPLE_RATE}")
        if self.tone_ms <= 0 or self.gap_ms < 0:
            raise ValueError("tone_ms must be > 0, gap_ms must be >= 0")

    def _samples_for(self, freq: float, ms: int) -> list[int]:
        n = int(self.sample_rate * ms / 1000)
        peak = int(self.amplitude * 32767)
        two_pi_f = 2 * math.pi * freq
        return [int(peak * math.sin(two_pi_f * t / self.sample_rate)) for t in range(n)]

    def _silence(self, ms: int) -> list[int]:
        return [0] * int(self.sample_rate * ms / 1000)

    def _render_sync(self, text: str) -> bytes:
        samples: list[int] = []
        pad = self._silence(self.gap_ms)
        samples.extend(pad)
        for ch in text:
            freq = self.tone_map.get(ch.lower(), self.fallback_freq)
            samples.extend(self._samples_for(freq, self.tone_ms))
            samples.extend(pad)

        buf = io.BytesIO()
        with wave.open(buf, "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(self.sample_rate)
            w.writeframes(struct.pack(f"<{len(samples)}h", *samples))
        return buf.getvalue()

    async def render(self, challenge: Challenge) -> bytes:
        return await asyncio.to_thread(self._render_sync, challenge.solution)


__all__ = ["AudioRenderer"]
