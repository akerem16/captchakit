"""Micro-benchmarks for captchakit.

Run with::

    uv run python benchmarks/bench.py

Output is a markdown table suitable for pasting into README.md.
"""

from __future__ import annotations

import asyncio
import statistics
import time
from collections.abc import Awaitable, Callable

from captchakit import (
    AudioRenderer,
    CaptchaManager,
    ImageRenderer,
    MemoryStorage,
    SVGRenderer,
    TextChallengeFactory,
)
from captchakit.challenges.base import Challenge

ITERATIONS = 500
WARMUP = 20


async def _time(coro_factory: Callable[[], Awaitable[object]]) -> list[float]:
    for _ in range(WARMUP):
        await coro_factory()
    samples: list[float] = []
    for _ in range(ITERATIONS):
        t0 = time.perf_counter()
        await coro_factory()
        samples.append((time.perf_counter() - t0) * 1000)
    return samples


def _summary(samples: list[float]) -> tuple[float, float, float]:
    return (
        statistics.mean(samples),
        statistics.median(samples),
        statistics.quantiles(samples, n=100)[98],  # p99
    )


async def bench_image_renderer() -> list[float]:
    renderer = ImageRenderer(width=220, height=80, font_size=40)
    challenge = Challenge(id="x", prompt="ABCDE", solution="ABCDE", created_at=0.0, expires_at=1e9)
    return await _time(lambda: renderer.render(challenge))


async def bench_svg_renderer() -> list[float]:
    renderer = SVGRenderer(width=220, height=80, font_size=40)
    challenge = Challenge(id="x", prompt="ABCDE", solution="ABCDE", created_at=0.0, expires_at=1e9)
    return await _time(lambda: renderer.render(challenge))


async def bench_audio_renderer() -> list[float]:
    renderer = AudioRenderer(sample_rate=16000, tone_ms=200, gap_ms=100)
    challenge = Challenge(id="x", prompt="12345", solution="12345", created_at=0.0, expires_at=1e9)
    return await _time(lambda: renderer.render(challenge))


async def bench_issue_verify_roundtrip() -> list[float]:
    manager = CaptchaManager(
        factory=TextChallengeFactory(length=5),
        renderer=ImageRenderer(width=160, height=60, font_size=28),
        storage=MemoryStorage(),
        ttl=60.0,
    )

    async def _run() -> None:
        cid, _ = await manager.issue()
        ch = await manager.storage.get(cid)
        assert ch is not None
        await manager.verify(cid, ch.solution)

    return await _time(_run)


async def main() -> None:
    print("Running benchmarks...")
    cases = {
        "ImageRenderer.render (PNG)": await bench_image_renderer(),
        "SVGRenderer.render (SVG)": await bench_svg_renderer(),
        "AudioRenderer.render (WAV)": await bench_audio_renderer(),
        "issue + verify roundtrip": await bench_issue_verify_roundtrip(),
    }

    print(f"\n{ITERATIONS} iterations, {WARMUP} warmup\n")
    print("| Operation | Mean (ms) | Median (ms) | p99 (ms) |")
    print("|-----------|----------:|------------:|---------:|")
    for name, samples in cases.items():
        mean, median, p99 = _summary(samples)
        print(f"| `{name}` | {mean:.2f} | {median:.2f} | {p99:.2f} |")


if __name__ == "__main__":
    asyncio.run(main())
