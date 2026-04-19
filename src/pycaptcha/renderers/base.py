"""Renderer protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pycaptcha.challenges.base import Challenge


@runtime_checkable
class Renderer(Protocol):
    """Turns a :class:`Challenge` into bytes (typically an image)."""

    content_type: str

    async def render(self, challenge: Challenge) -> bytes:  # pragma: no cover - protocol
        ...
