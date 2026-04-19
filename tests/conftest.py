"""Shared fixtures."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from pycaptcha import (
    CaptchaManager,
    ImageRenderer,
    MathChallengeFactory,
    MemoryStorage,
    TextChallengeFactory,
)


@dataclass
class FakeClock:
    """Deterministic clock used to exercise TTL / expiry logic."""

    t: float = 1000.0

    def now(self) -> float:
        return self.t

    def advance(self, dt: float) -> None:
        self.t += dt


@pytest.fixture
def clock() -> FakeClock:
    return FakeClock()


@pytest.fixture
def renderer() -> ImageRenderer:
    return ImageRenderer(width=160, height=60, font_size=28)


@pytest.fixture
def storage(clock: FakeClock) -> MemoryStorage:
    return MemoryStorage(clock=clock)


@pytest.fixture
def text_manager(
    clock: FakeClock, renderer: ImageRenderer, storage: MemoryStorage
) -> CaptchaManager:
    return CaptchaManager(
        factory=TextChallengeFactory(length=5),
        renderer=renderer,
        storage=storage,
        ttl=60.0,
        max_attempts=3,
        clock=clock,
    )


@pytest.fixture
def math_manager(
    clock: FakeClock, renderer: ImageRenderer, storage: MemoryStorage
) -> CaptchaManager:
    return CaptchaManager(
        factory=MathChallengeFactory(),
        renderer=renderer,
        storage=storage,
        ttl=60.0,
        max_attempts=3,
        clock=clock,
    )
