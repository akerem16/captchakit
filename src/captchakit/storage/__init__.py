"""Challenge storage backends."""

from __future__ import annotations

from typing import TYPE_CHECKING

from captchakit.storage.base import Storage
from captchakit.storage.memory import MemoryStorage

if TYPE_CHECKING:
    from captchakit.storage.postgres import PostgresStorage
    from captchakit.storage.redis import RedisStorage

__all__ = ["MemoryStorage", "PostgresStorage", "RedisStorage", "Storage"]


def __getattr__(name: str) -> object:
    # Lazily expose backend classes so users who haven't installed the
    # matching extra can still `from captchakit.storage import MemoryStorage`
    # without hitting ImportError at import time.
    if name == "RedisStorage":
        from captchakit.storage.redis import RedisStorage  # noqa: PLC0415

        return RedisStorage
    if name == "PostgresStorage":
        from captchakit.storage.postgres import PostgresStorage  # noqa: PLC0415

        return PostgresStorage
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
