"""Generate the README showcase gallery.

Renders one sample per built-in :class:`Theme` plus an SVG and WAV sample
into ``docs/assets/showcase/``. The visual samples use a fixed solution
("HUMAN", "python") so the images are reproducible across runs; the
math sample draws a fresh prompt each time (cosmetic churn only).

Run from the repo root::

    uv run python scripts/render_showcase.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from captchakit import (
    AudioRenderer,
    Challenge,
    ImageRenderer,
    MathChallengeFactory,
    SVGRenderer,
    TextChallengeFactory,
    Theme,
)

OUT = Path(__file__).resolve().parent.parent / "docs" / "assets" / "showcase"


def _fake_challenge(prompt: str, solution: str) -> Challenge:
    return Challenge(
        id="showcase",
        prompt=prompt,
        solution=solution,
        case_sensitive=False,
        created_at=0.0,
        expires_at=120.0,
    )


async def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    themes: dict[str, Theme] = {
        "classic": Theme.CLASSIC,
        "dark": Theme.DARK,
        "pastel": Theme.PASTEL,
        "high_contrast": Theme.HIGH_CONTRAST,
    }

    text_challenge = _fake_challenge("HUMAN", "HUMAN")
    for name, theme in themes.items():
        renderer = ImageRenderer(theme=theme)
        png = await renderer.render(text_challenge)
        (OUT / f"text_{name}.png").write_bytes(png)

    math_factory = MathChallengeFactory(operators=("+", "-"), min_operand=1, max_operand=9)
    math_spec = await math_factory.create()
    math_challenge = _fake_challenge(math_spec.prompt, math_spec.solution)
    (OUT / "math_classic.png").write_bytes(
        await ImageRenderer(theme=Theme.CLASSIC).render(math_challenge)
    )

    word_challenge = _fake_challenge("python", "python")
    svg_bytes = await SVGRenderer().render(word_challenge)
    (OUT / "word_svg.svg").write_bytes(svg_bytes)

    text_factory = TextChallengeFactory(length=5)
    text_spec = await text_factory.create()
    audio_challenge = _fake_challenge(text_spec.prompt, text_spec.solution)
    wav_bytes = await AudioRenderer().render(audio_challenge)
    (OUT / "accessibility.wav").write_bytes(wav_bytes)

    for path in sorted(OUT.iterdir()):
        print(f"wrote {path.relative_to(OUT.parent.parent.parent)}  ({path.stat().st_size} B)")


if __name__ == "__main__":
    asyncio.run(main())
