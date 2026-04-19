"""Challenge storage backends."""

from __future__ import annotations

from captchakit.storage.base import Storage
from captchakit.storage.memory import MemoryStorage

__all__ = ["MemoryStorage", "Storage"]
