from __future__ import annotations

from captchakit import Challenge, MemoryStorage

from .conftest import FakeClock


def _ch(cid: str, expires_at: float = 1000.0) -> Challenge:
    return Challenge(
        id=cid,
        prompt="p",
        solution="s",
        created_at=0.0,
        expires_at=expires_at,
    )


async def test_put_get_delete(storage: MemoryStorage) -> None:
    ch = _ch("a")
    await storage.put(ch)
    assert await storage.get("a") == ch
    await storage.delete("a")
    assert await storage.get("a") is None


async def test_get_missing_returns_none(storage: MemoryStorage) -> None:
    assert await storage.get("nope") is None


async def test_incr_attempts_zero_when_missing(storage: MemoryStorage) -> None:
    assert await storage.incr_attempts("missing") == 0


async def test_incr_attempts_increments(storage: MemoryStorage) -> None:
    await storage.put(_ch("a"))
    assert await storage.incr_attempts("a") == 1
    assert await storage.incr_attempts("a") == 2
    assert await storage.incr_attempts("a") == 3


async def test_cleanup_expired(clock: FakeClock, storage: MemoryStorage) -> None:
    clock.t = 100.0
    await storage.put(_ch("old", expires_at=50.0))
    await storage.put(_ch("new", expires_at=200.0))
    removed = await storage.cleanup_expired()
    assert removed == 1
    assert await storage.get("old") is None
    assert await storage.get("new") is not None


async def test_size(storage: MemoryStorage) -> None:
    assert await storage.size() == 0
    await storage.put(_ch("a"))
    await storage.put(_ch("b"))
    assert await storage.size() == 2
