"""Smoke tests for PostgresStorage.

These tests require a reachable Postgres server. Set ``CAPTCHAKIT_PG_DSN``
in the environment (e.g.
``postgres://postgres:postgres@localhost:5432/postgres``) to enable them;
otherwise the module is skipped entirely. CI does not exercise this
backend — we only validate against the import-time contract.
"""

from __future__ import annotations

import os

import pytest

asyncpg = pytest.importorskip("asyncpg")

pytestmark = pytest.mark.skipif(
    "CAPTCHAKIT_PG_DSN" not in os.environ,
    reason="set CAPTCHAKIT_PG_DSN to run Postgres integration tests",
)

from captchakit.challenges.base import Challenge  # noqa: E402
from captchakit.storage.postgres import PostgresStorage  # noqa: E402


@pytest.fixture
async def storage():
    dsn = os.environ["CAPTCHAKIT_PG_DSN"]
    pool = await asyncpg.create_pool(dsn=dsn, min_size=1, max_size=2)
    s = PostgresStorage(pool=pool, table="captchakit_test_challenges")
    await s.create_schema()
    async with pool.acquire() as conn:
        await conn.execute(f"TRUNCATE {s.table}")
    yield s
    await pool.close()


async def test_put_get_roundtrip(storage) -> None:
    ch = Challenge(
        id="abc123",
        prompt="HELLO",
        solution="HELLO",
        created_at=0.0,
        expires_at=9999999999.0,
    )
    await storage.put(ch)
    loaded = await storage.get(ch.id)
    assert loaded is not None
    assert loaded.solution == "HELLO"


async def test_incr_attempts(storage) -> None:
    ch = Challenge(
        id="xyz",
        prompt="X",
        solution="X",
        created_at=0.0,
        expires_at=9999999999.0,
    )
    await storage.put(ch)
    assert await storage.incr_attempts(ch.id) == 1
    assert await storage.incr_attempts(ch.id) == 2
    assert await storage.incr_attempts("missing") == 0


async def test_delete(storage) -> None:
    ch = Challenge(
        id="del",
        prompt="X",
        solution="X",
        created_at=0.0,
        expires_at=9999999999.0,
    )
    await storage.put(ch)
    await storage.delete(ch.id)
    assert await storage.get(ch.id) is None


async def test_cleanup_expired(storage) -> None:
    live = Challenge(id="live", prompt="X", solution="X", created_at=0.0, expires_at=9e9)
    dead = Challenge(id="dead", prompt="X", solution="X", created_at=0.0, expires_at=-1e9)
    await storage.put(live)
    await storage.put(dead)
    removed = await storage.cleanup_expired()
    assert removed >= 1
    assert await storage.get("dead") is None
    assert await storage.get("live") is not None
