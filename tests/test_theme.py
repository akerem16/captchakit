from __future__ import annotations

import pytest

from captchakit import ImageRenderer, Theme
from captchakit.challenges.base import Challenge


def _challenge() -> Challenge:
    return Challenge(
        id="x",
        prompt="ABCDE",
        solution="ABCDE",
        created_at=0.0,
        expires_at=1000.0,
    )


def test_theme_presets_have_non_empty_palette() -> None:
    for preset in (Theme.CLASSIC, Theme.DARK, Theme.PASTEL, Theme.HIGH_CONTRAST):
        assert preset.palette
        assert preset.noise_lines >= 0


def test_theme_rejects_empty_palette() -> None:
    with pytest.raises(ValueError):
        Theme(palette=())


def test_theme_rejects_negative_noise() -> None:
    with pytest.raises(ValueError):
        Theme(noise_lines=-1)


async def test_renderer_uses_theme_background() -> None:
    renderer = ImageRenderer(width=120, height=40, font_size=20, theme=Theme.HIGH_CONTRAST)
    png = await renderer.render(_challenge())
    assert png.startswith(b"\x89PNG")
    assert renderer.bg_color == (255, 255, 255)
    assert renderer.noise_lines == 0


async def test_renderer_dark_theme_renders() -> None:
    renderer = ImageRenderer(width=120, height=40, font_size=20, theme=Theme.DARK)
    png = await renderer.render(_challenge())
    assert png.startswith(b"\x89PNG")
