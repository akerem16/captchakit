"""Pillow-backed image renderer.

CPU-bound drawing is offloaded to a worker thread via :func:`asyncio.to_thread`
so callers can treat the renderer as fully async.
"""

from __future__ import annotations

import asyncio
import random
import secrets
from dataclasses import dataclass, field
from io import BytesIO
from pathlib import Path
from typing import TYPE_CHECKING

from PIL import Image, ImageDraw, ImageFont

if TYPE_CHECKING:
    from pycaptcha.challenges.base import Challenge

RGB = tuple[int, int, int]


def _default_palette() -> tuple[RGB, ...]:
    return (
        (30, 30, 30),
        (60, 20, 120),
        (20, 80, 40),
        (140, 30, 40),
        (10, 60, 100),
    )


@dataclass(slots=True)
class ImageRenderer:
    """Renders a challenge's prompt into a PNG.

    The renderer is intentionally simple: it draws the prompt glyph-by-glyph
    with small random rotations / offsets and a few decorative lines. It is
    *not* meant to defeat OCR — it's a light human-check layer (see SECURITY
    notes in the README).
    """

    width: int = 220
    height: int = 80
    padding: int = 10
    font_size: int = 40
    font_path: str | Path | None = None
    bg_color: RGB = (245, 245, 245)
    palette: tuple[RGB, ...] = field(default_factory=_default_palette)
    noise_lines: int = 4
    content_type: str = "image/png"

    def _load_font(self) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
        if self.font_path is not None:
            return ImageFont.truetype(str(self.font_path), self.font_size)
        return ImageFont.load_default(size=self.font_size)

    def _render_sync(self, text: str) -> bytes:
        rng = random.Random(secrets.randbits(64))
        img = Image.new("RGB", (self.width, self.height), self.bg_color)
        draw = ImageDraw.Draw(img)
        font = self._load_font()

        for _ in range(self.noise_lines):
            x1 = rng.randint(0, self.width)
            y1 = rng.randint(0, self.height)
            x2 = rng.randint(0, self.width)
            y2 = rng.randint(0, self.height)
            draw.line((x1, y1, x2, y2), fill=rng.choice(self.palette), width=1)

        inner_w = self.width - 2 * self.padding
        n = max(len(text), 1)
        step = inner_w / n
        for idx, ch in enumerate(text):
            glyph = Image.new("RGBA", (self.font_size + 16, self.font_size + 16), (0, 0, 0, 0))
            gdraw = ImageDraw.Draw(glyph)
            gdraw.text((8, 4), ch, font=font, fill=rng.choice(self.palette))
            angle = rng.uniform(-25, 25)
            rotated = glyph.rotate(angle, resample=Image.Resampling.BICUBIC, expand=False)
            x = int(self.padding + idx * step + rng.uniform(-2, 2))
            y = int((self.height - rotated.height) / 2 + rng.uniform(-4, 4))
            img.paste(rotated, (x, y), rotated)

        buf = BytesIO()
        img.save(buf, format="PNG", optimize=True)
        return buf.getvalue()

    async def render(self, challenge: Challenge) -> bytes:
        return await asyncio.to_thread(self._render_sync, challenge.prompt)
