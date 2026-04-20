from __future__ import annotations

import pytest

from captchakit import (
    CaptchaManager,
    ImageRenderer,
    MemoryStorage,
    NoOpRateLimiter,
    RateLimited,
    RateLimiter,
    TextChallengeFactory,
    TokenBucketRateLimiter,
)

from .conftest import FakeClock


def test_noop_is_a_rate_limiter() -> None:
    assert isinstance(NoOpRateLimiter(), RateLimiter)


def test_token_bucket_rejects_bad_config() -> None:
    with pytest.raises(ValueError):
        TokenBucketRateLimiter(capacity=0)
    with pytest.raises(ValueError):
        TokenBucketRateLimiter(refill_rate=0)


async def test_token_bucket_allows_within_capacity(clock: FakeClock) -> None:
    limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1, clock=clock)
    for _ in range(3):
        await limiter.acquire("user-a")


async def test_token_bucket_rejects_beyond_capacity(clock: FakeClock) -> None:
    limiter = TokenBucketRateLimiter(capacity=2, refill_rate=1, clock=clock)
    await limiter.acquire("user-a")
    await limiter.acquire("user-a")
    with pytest.raises(RateLimited) as exc_info:
        await limiter.acquire("user-a")
    assert exc_info.value.key == "user-a"
    assert exc_info.value.retry_after is not None
    assert exc_info.value.retry_after > 0


async def test_token_bucket_refills_over_time(clock: FakeClock) -> None:
    limiter = TokenBucketRateLimiter(capacity=1, refill_rate=1, clock=clock)
    await limiter.acquire("u")
    with pytest.raises(RateLimited):
        await limiter.acquire("u")
    clock.advance(1.5)
    await limiter.acquire("u")  # refilled


async def test_token_bucket_is_per_key(clock: FakeClock) -> None:
    limiter = TokenBucketRateLimiter(capacity=1, refill_rate=0.01, clock=clock)
    await limiter.acquire("alice")
    await limiter.acquire("bob")  # different bucket, still has tokens


async def test_manager_propagates_rate_limited(clock: FakeClock) -> None:
    limiter = TokenBucketRateLimiter(capacity=1, refill_rate=0.01, clock=clock)
    mgr = CaptchaManager(
        factory=TextChallengeFactory(length=4),
        renderer=ImageRenderer(width=120, height=40, font_size=20),
        storage=MemoryStorage(clock=clock),
        ttl=30.0,
        clock=clock,
        rate_limiter=limiter,
    )
    await mgr.issue(key="1.2.3.4")
    with pytest.raises(RateLimited):
        await mgr.issue(key="1.2.3.4")
    # Different key still allowed.
    await mgr.issue(key="5.6.7.8")
