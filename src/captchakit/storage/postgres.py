"""PostgreSQL-backed storage.

Install with ``pip install "captchakit[postgres]"``. Uses a single table
with ``challenge_id`` primary key, JSONB payload and a ``timestamptz``
expiration column. Multi-process and multi-host safe.

Postgres has no native per-row TTL, so :class:`PostgresStorage` checks
``expires_at`` on every ``get`` and exposes
:meth:`cleanup_expired` for periodic eviction. Call it from a background
task (e.g. APScheduler, Celery beat, or ``asyncio.create_task`` + sleep)
every minute or two.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any

try:
    import asyncpg
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "Postgres storage requires the `postgres` extra: pip install 'captchakit[postgres]'"
    ) from exc

from captchakit._clock import Clock, MonotonicClock
from captchakit.challenges.base import Challenge

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS {table} (
    challenge_id   TEXT PRIMARY KEY,
    data           JSONB NOT NULL,
    attempts       INTEGER NOT NULL DEFAULT 0,
    expires_at     TIMESTAMPTZ NOT NULL
);
CREATE INDEX IF NOT EXISTS {table}_expires_at_idx
    ON {table} (expires_at);
"""


def _unix_to_dt(ts: float) -> datetime:
    return datetime.fromtimestamp(ts, tz=timezone.utc)


@dataclass(slots=True)
class PostgresStorage:
    """Stores challenges in a single Postgres table.

    ``pool`` must be an already-connected :class:`asyncpg.Pool`. Call
    :meth:`create_schema` once at application startup to create the
    table and index (idempotent — safe to run on every boot).

    ``wall_clock_offset`` is a compatibility shim: the captcha manager's
    :class:`Clock` is monotonic by default, but Postgres stores wall-clock
    timestamps. The offset is captured on the first ``put`` and used to
    translate monotonic timestamps into UTC datetimes consistently.
    """

    pool: asyncpg.Pool
    table: str = "captchakit_challenges"
    clock: Clock = field(default_factory=MonotonicClock)
    _wall_offset: float | None = field(default=None, init=False, repr=False)

    def _to_wall(self, ts: float) -> datetime:
        if self._wall_offset is None:
            import time  # noqa: PLC0415

            self._wall_offset = time.time() - self.clock.now()
        return _unix_to_dt(ts + self._wall_offset)

    async def create_schema(self) -> None:
        """Create the challenges table and index if they don't exist."""
        async with self.pool.acquire() as conn:
            await conn.execute(SCHEMA_SQL.format(table=self.table))

    async def put(self, challenge: Challenge) -> None:
        payload = json.dumps(asdict(challenge))
        await self.pool.execute(
            f"INSERT INTO {self.table} (challenge_id, data, expires_at) "
            f"VALUES ($1, $2::jsonb, $3) "
            f"ON CONFLICT (challenge_id) DO UPDATE "
            f"SET data = EXCLUDED.data, expires_at = EXCLUDED.expires_at, attempts = 0",
            challenge.id,
            payload,
            self._to_wall(challenge.expires_at),
        )

    async def get(self, challenge_id: str) -> Challenge | None:
        row = await self.pool.fetchrow(
            f"SELECT data FROM {self.table} WHERE challenge_id = $1",
            challenge_id,
        )
        if row is None:
            return None
        data: dict[str, Any] = json.loads(row["data"])
        return Challenge(**data)

    async def delete(self, challenge_id: str) -> None:
        await self.pool.execute(
            f"DELETE FROM {self.table} WHERE challenge_id = $1",
            challenge_id,
        )

    async def incr_attempts(self, challenge_id: str) -> int:
        row = await self.pool.fetchrow(
            f"UPDATE {self.table} SET attempts = attempts + 1 "
            f"WHERE challenge_id = $1 RETURNING attempts",
            challenge_id,
        )
        if row is None:
            return 0
        return int(row["attempts"])

    async def cleanup_expired(self) -> int:
        """Delete rows whose ``expires_at`` is in the past. Returns count."""
        result = await self.pool.execute(f"DELETE FROM {self.table} WHERE expires_at < now()")
        return int(result.split()[-1]) if result.startswith("DELETE") else 0


__all__ = ["PostgresStorage"]
