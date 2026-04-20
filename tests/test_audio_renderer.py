from __future__ import annotations

import io
import wave

import pytest

from captchakit import AudioRenderer
from captchakit.challenges.base import Challenge


def _challenge(solution: str = "ab12") -> Challenge:
    return Challenge(
        id="x",
        prompt=solution,
        solution=solution,
        created_at=0.0,
        expires_at=1000.0,
    )


async def test_audio_output_is_valid_wav() -> None:
    renderer = AudioRenderer(sample_rate=8000, tone_ms=50, gap_ms=20)
    data = await renderer.render(_challenge("123"))
    assert data.startswith(b"RIFF")
    with wave.open(io.BytesIO(data), "rb") as w:
        assert w.getnchannels() == 1
        assert w.getsampwidth() == 2
        assert w.getframerate() == 8000
        assert w.getnframes() > 0


async def test_audio_length_scales_with_input() -> None:
    r = AudioRenderer(sample_rate=8000, tone_ms=100, gap_ms=50)
    short = await r.render(_challenge("a"))
    long = await r.render(_challenge("abcde"))
    assert len(long) > len(short)


async def test_unknown_chars_use_fallback() -> None:
    r = AudioRenderer(sample_rate=8000, tone_ms=30, gap_ms=10)
    data = await r.render(_challenge("???"))
    with wave.open(io.BytesIO(data), "rb") as w:
        assert w.getnframes() > 0


def test_audio_rejects_bad_params() -> None:
    with pytest.raises(ValueError):
        AudioRenderer(amplitude=0)
    with pytest.raises(ValueError):
        AudioRenderer(amplitude=2.0)
    with pytest.raises(ValueError):
        AudioRenderer(sample_rate=1000)
    with pytest.raises(ValueError):
        AudioRenderer(tone_ms=0)
    with pytest.raises(ValueError):
        AudioRenderer(gap_ms=-1)


def test_audio_content_type() -> None:
    assert AudioRenderer().content_type == "audio/wav"
