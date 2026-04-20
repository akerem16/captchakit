"""Theme presets for :class:`captchakit.renderers.ImageRenderer`.

A :class:`Theme` bundles background colour, glyph palette, noise density
and optional font path. Four built-in presets cover the common needs;
pass your own :class:`Theme` for anything else::

    from captchakit import ImageRenderer, Theme
    renderer = ImageRenderer(theme=Theme.DARK)

    my_theme = Theme(
        bg_color=(255, 240, 220),
        palette=((80, 40, 10), (140, 70, 20)),
        noise_lines=6,
    )
    renderer = ImageRenderer(theme=my_theme)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import ClassVar

RGB = tuple[int, int, int]


@dataclass(frozen=True, slots=True)
class Theme:
    """Visual style for the image renderer.

    Attributes:
        bg_color: Canvas background colour (RGB).
        palette: Glyph and noise-line colours. At least one entry.
        noise_lines: Random decorative lines drawn behind the glyphs.
        font_path: Optional TrueType font path; ``None`` uses Pillow's default.
    """

    bg_color: RGB = (245, 245, 245)
    palette: tuple[RGB, ...] = field(
        default_factory=lambda: (
            (30, 30, 30),
            (60, 20, 120),
            (20, 80, 40),
            (140, 30, 40),
            (10, 60, 100),
        )
    )
    noise_lines: int = 4
    font_path: str | Path | None = None

    CLASSIC: ClassVar[Theme]
    DARK: ClassVar[Theme]
    PASTEL: ClassVar[Theme]
    HIGH_CONTRAST: ClassVar[Theme]

    def __post_init__(self) -> None:
        if not self.palette:
            raise ValueError("palette must be non-empty")
        if self.noise_lines < 0:
            raise ValueError("noise_lines must be >= 0")


Theme.CLASSIC = Theme()
Theme.DARK = Theme(
    bg_color=(18, 18, 24),
    palette=(
        (230, 230, 230),
        (180, 200, 255),
        (255, 180, 180),
        (180, 255, 210),
        (255, 220, 150),
    ),
    noise_lines=3,
)
Theme.PASTEL = Theme(
    bg_color=(250, 245, 240),
    palette=(
        (190, 120, 140),
        (120, 160, 190),
        (150, 180, 130),
        (210, 170, 110),
        (160, 140, 190),
    ),
    noise_lines=5,
)
# WCAG AA: pure black on pure white, no distracting noise.
Theme.HIGH_CONTRAST = Theme(
    bg_color=(255, 255, 255),
    palette=((0, 0, 0),),
    noise_lines=0,
)


__all__ = ["Theme"]
