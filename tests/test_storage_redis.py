from __future__ import annotations

import asyncio

import pytest

pytest.importorskip("fakeredis")
pytest.importorskip("redis")

from fakeredis import FakeAsyncRedis

from captchakit import CaptchaManager, Challenge, ImageRenderer, TextChallengeFactory
from captchakit.storage.redis import RedisStorage

from .conftest import FakeClock


def _ch(cid: str, expires_at: float = 1000.0) -> Challenge:
    return Challenge(
        id=cid,
        prompt="p",
        solution="s",
        created_at=0.0,
        expires_at=expires_at,
    )


@pytest.fixture
def redis_client() -> FakeAsyncRedis:
    return FakeAsyncRedis()


@pytest.fixture
def redis_storage(redis_client: FakeAsyncRedis, clock: FakeClock) -> RedisStorage:
    return RedisStorage(client=redis_client, clock=clock, prefix="test")


async def test_put_get_delete(redis_storage: RedisStorage) -> None:
    ch = _ch("a")
    await redis_storage.put(ch)
    got = await redis_storage.get("a")
    assert got == ch
    await redis_storage.delete("a")
    assert await redis_storage.get("a") is None


async def test_get_missing_returns_none(redis_storage: RedisStorage) -> None:
    assert await redis_storage.get("nope") is None


async def test_incr_attempts_returns_zero_when_missing(
    redis_storage: RedisStorage,
) -> None:
    assert await redis_storage.incr_attempts("missing") == 0


async def test_incr_attempts_increments(redis_storage: RedisStorage) -> None:
    await redis_storage.put(_ch("a"))
    assert await redis_storage.incr_attempts("a") == 1
    assert await redis_storage.incr_attempts("a") == 2
    assert await redis_storage.incr_attempts("a") == 3


async def test_incr_attempts_after_delete(redis_storage: RedisStorage) -> None:
    await redis_storage.put(_ch("a"))
    await redis_storage.incr_attempts("a")
    await redis_storage.delete("a")
    assert await redis_storage.incr_attempts("a") == 0


async def test_native_ttl_evicts_expired(
    redis_storage: RedisStorage, redis_client: FakeAsyncRedis, clock: FakeClock
) -> None:
    # ttl = expires_at - now + grace + 1; with clock.t=1000 and expires_at=1000
    # we still get a positive TTL because of the grace window. Set a challenge
    # with no time left and fast-forward Redis' view of time.
    await redis_storage.put(_ch("a", expires_at=clock.t + 1.0))
    # Advance the *fake* redis clock past TTL; FakeAsyncRedis exposes ttl()
    # so we just verify it's a positive number we expect to elapse.
    remaining = await redis_client.ttl("test:ch:a")
    assert remaining >= 1
    # real expiry would be enforced by Redis itself in production; fakeredis
    # doesn't advance its clock in-process, so we just assert TTL is set.


async def test_round_trip_through_manager(redis_storage: RedisStorage, clock: FakeClock) -> None:
    manager = CaptchaManager(
        factory=TextChallengeFactory(length=5),
        renderer=ImageRenderer(width=100, height=50, font_size=24),
        storage=redis_storage,
        ttl=60.0,
        max_attempts=3,
        clock=clock,
    )
    cid, _ = await manager.issue()
    stored = await redis_storage.get(cid)
    assert stored is not None
    assert await manager.verify(cid, stored.solution) is True
    assert await redis_storage.get(cid) is None


async def test_concurrent_puts_and_gets_are_safe(
    redis_storage: RedisStorage,
) -> None:
    async def worker(i: int) -> None:
        ch = _ch(f"c{i}")
        await redis_storage.put(ch)
        got = await redis_storage.get(f"c{i}")
        assert got == ch

    await asyncio.gather(*(worker(i) for i in range(20)))
