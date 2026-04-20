"""Pure-Python SVG renderer.

Generates vector output — roughly 10x smaller than the equivalent PNG
and scales losslessly on high-DPI screens. No Pillow dependency.

The rendering loop draws the challenge prompt glyph-by-glyph with small
random rotations / colours drawn from the active :class:`Theme`, plus a
few decorative noise lines. Output is a UTF-8 encoded ``image/svg+xml``
byte-string.
"""

from __future__ import annotations

import random
import secrets
from dataclasses import dataclass, field
from html import escape
from typing import TYPE_CHECKING

from captchakit.renderers.theme import Theme

if TYPE_CHECKING:
    from captchakit.challenges.base import Challenge

RGB = tuple[int, int, int]


def _rgb(color: RGB) -> str:
    return f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"


@dataclass(slots=True)
class SVGRenderer:
    """Renders a challenge's prompt into an SVG byte-string.

    Like :class:`ImageRenderer`, this is a lightweight human-check —
    not an OCR-defeating captcha. Combine with rate-limiting.
    """

    width: int = 220
    height: int = 80
    padding: int = 10
    font_size: int = 40
    theme: Theme = field(default_factory=lambda: Theme.CLASSIC)
    font_family: str = "sans-serif"
    content_type: str = "image/svg+xml"

    async def render(self, challenge: Challenge) -> bytes:
        return self._render_sync(challenge.prompt).encode("utf-8")

    def _render_sync(self, text: str) -> str:
        rng = random.Random(secrets.randbits(64))
        palette = self.theme.palette
        parts: list[str] = [
            f'<svg xmlns="http://www.w3.org/2000/svg" '
            f'width="{self.width}" height="{self.height}" '
            f'viewBox="0 0 {self.width} {self.height}">',
            f'<rect width="100%" height="100%" fill="{_rgb(self.theme.bg_color)}"/>',
        ]

        for _ in range(self.theme.noise_lines):
            x1 = rng.randint(0, self.width)
            y1 = rng.randint(0, self.height)
            x2 = rng.randint(0, self.width)
            y2 = rng.randint(0, self.height)
            parts.append(
                f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                f'stroke="{_rgb(rng.choice(palette))}" stroke-width="1"/>'
            )

        inner_w = self.width - 2 * self.padding
        n = max(len(text), 1)
        step = inner_w / n
        baseline_y = int(self.height / 2 + self.font_size / 3)
        for idx, ch in enumerate(text):
            cx = int(self.padding + idx * step + step / 2 + rng.uniform(-2, 2))
            cy = int(baseline_y + rng.uniform(-4, 4))
            angle = rng.uniform(-25, 25)
            color = rng.choice(palette)
            parts.append(
                f'<text x="{cx}" y="{cy}" '
                f'font-family="{escape(self.font_family)}" '
                f'font-size="{self.font_size}" '
                f'fill="{_rgb(color)}" text-anchor="middle" '
                f'transform="rotate({angle:.1f} {cx} {cy})">'
                f"{escape(ch)}"
                f"</text>"
            )

        parts.append("</svg>")
        return "".join(parts)


__all__ = ["SVGRenderer"]
