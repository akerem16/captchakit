from __future__ import annotations

from captchakit import SVGRenderer, Theme
from captchakit.challenges.base import Challenge


def _challenge(prompt: str = "ABCDE") -> Challenge:
    return Challenge(
        id="x",
        prompt=prompt,
        solution=prompt,
        created_at=0.0,
        expires_at=1000.0,
    )


async def test_svg_output_is_valid_xml_bytes() -> None:
    renderer = SVGRenderer(width=160, height=60, font_size=28)
    data = await renderer.render(_challenge())
    assert isinstance(data, bytes)
    text = data.decode("utf-8")
    assert text.startswith("<svg")
    assert text.endswith("</svg>")
    assert 'xmlns="http://www.w3.org/2000/svg"' in text


async def test_svg_contains_each_character() -> None:
    renderer = SVGRenderer()
    data = await renderer.render(_challenge("HELLO"))
    text = data.decode("utf-8")
    for ch in "HELLO":
        assert f">{ch}<" in text


async def test_svg_escapes_special_characters() -> None:
    renderer = SVGRenderer()
    data = await renderer.render(_challenge("<&>"))
    text = data.decode("utf-8")
    assert ">&lt;<" in text
    assert ">&amp;<" in text
    assert ">&gt;<" in text


async def test_svg_respects_theme_noise() -> None:
    renderer = SVGRenderer(theme=Theme.HIGH_CONTRAST)
    data = await renderer.render(_challenge())
    text = data.decode("utf-8")
    assert "<line" not in text


async def test_svg_content_type() -> None:
    assert SVGRenderer().content_type == "image/svg+xml"
