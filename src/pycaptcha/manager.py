"""High-level orchestrator: issue, verify, cleanup."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from pycaptcha._clock import Clock, MonotonicClock
from pycaptcha.challenges.base import Challenge, ChallengeFactory
from pycaptcha.errors import ChallengeExpired, ChallengeNotFound, TooManyAttempts
from pycaptcha.renderers.base import Renderer
from pycaptcha.storage.base import Storage


@dataclass(slots=True)
class CaptchaManager:
    """Coordinates a :class:`ChallengeFactory`, :class:`Renderer` and :class:`Storage`.

    Typical usage::

        manager = CaptchaManager(
            factory=TextChallengeFactory(),
            renderer=ImageRenderer(),
            storage=MemoryStorage(),
            ttl=120.0,
        )
        challenge_id, png = await manager.issue()
        ...
        ok = await manager.verify(challenge_id, user_input)
    """

    factory: ChallengeFactory
    renderer: Renderer
    storage: Storage
    ttl: float = 120.0
    max_attempts: int = 3
    clock: Clock = field(default_factory=MonotonicClock)

    def __post_init__(self) -> None:
        if self.ttl <= 0:
            raise ValueError("ttl must be > 0")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be >= 1")

    async def issue(self) -> tuple[str, bytes]:
        """Create and persist a fresh challenge, return ``(id, image_bytes)``."""
        spec = await self.factory.create()
        now = self.clock.now()
        challenge = Challenge(
            id=uuid4().hex,
            prompt=spec.prompt,
            solution=spec.solution,
            case_sensitive=spec.case_sensitive,
            created_at=now,
            expires_at=now + self.ttl,
        )
        image = await self.renderer.render(challenge)
        await self.storage.put(challenge)
        return challenge.id, image

    async def verify(self, challenge_id: str, user_input: str) -> bool:
        """Check a user's answer.

        Returns:
            ``True`` if the answer matches (the challenge is then deleted),
            ``False`` if the answer is wrong but the user still has attempts left.

        Raises:
            ChallengeNotFound: No such challenge (already consumed, never issued,
                or evicted by TTL).
            ChallengeExpired: The challenge passed its expiration time.
            TooManyAttempts: This was the final attempt and it was wrong.
        """
        challenge = await self.storage.get(challenge_id)
        if challenge is None:
            raise ChallengeNotFound(challenge_id)
        if challenge.is_expired(self.clock.now()):
            await self.storage.delete(challenge_id)
            raise ChallengeExpired(challenge_id)
        attempts = await self.storage.incr_attempts(challenge_id)
        if challenge.check(user_input):
            await self.storage.delete(challenge_id)
            return True
        if attempts >= self.max_attempts:
            await self.storage.delete(challenge_id)
            raise TooManyAttempts(challenge_id)
        return False

    async def discard(self, challenge_id: str) -> None:
        """Remove a challenge without checking it (e.g. on user cancel)."""
        await self.storage.delete(challenge_id)
