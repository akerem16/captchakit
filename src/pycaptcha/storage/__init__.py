"""Challenge storage backends."""

from __future__ import annotations

from pycaptcha.storage.base import Storage
from pycaptcha.storage.memory import MemoryStorage

__all__ = ["MemoryStorage", "Storage"]
