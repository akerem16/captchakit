from __future__ import annotations

from io import BytesIO

from PIL import Image

from pycaptcha import Challenge, ImageRenderer


def _ch(text: str) -> Challenge:
    return Challenge(
        id="x",
        prompt=text,
        solution=text,
        created_at=0.0,
        expires_at=1.0,
    )


async def test_render_returns_valid_png() -> None:
    r = ImageRenderer(width=200, height=80)
    data = await r.render(_ch("HELLO"))
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    img = Image.open(BytesIO(data))
    assert img.size == (200, 80)
    assert img.format == "PNG"


async def test_content_type() -> None:
    assert ImageRenderer().content_type == "image/png"


async def test_two_renders_are_different_due_to_noise() -> None:
    r = ImageRenderer()
    ch = _ch("ABC12")
    a = await r.render(ch)
    b = await r.render(ch)
    # Same prompt, but noise/rotation randomness should produce different bytes
    assert a != b
