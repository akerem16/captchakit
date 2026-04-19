"""FastAPI adapter.

Install with ``pip install "captchakit[fastapi]"``.

Usage::

    from fastapi import FastAPI
    from captchakit import CaptchaManager, TextChallengeFactory, ImageRenderer, MemoryStorage
    from captchakit.adapters.fastapi import captcha_router, verify_captcha

    manager = CaptchaManager(
        factory=TextChallengeFactory(),
        renderer=ImageRenderer(),
        storage=MemoryStorage(),
    )
    app = FastAPI()
    app.include_router(captcha_router(manager, prefix="/captcha"))

    @app.post("/register")
    async def register(_: None = Depends(verify_captcha(manager))):
        return {"ok": True}
"""

from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Annotated, Any

try:
    from fastapi import APIRouter, Depends, Form, HTTPException, Response, status
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "FastAPI adapter requires the `fastapi` extra: pip install 'captchakit[fastapi]'"
    ) from exc

from captchakit.errors import (
    ChallengeExpired,
    ChallengeNotFound,
    TooManyAttempts,
)

if TYPE_CHECKING:
    from collections.abc import Callable, Coroutine

    from captchakit.manager import CaptchaManager


def captcha_router(
    manager: CaptchaManager,
    *,
    prefix: str = "/captcha",
    tags: list[str] | None = None,
) -> APIRouter:
    """Build an :class:`APIRouter` that exposes ``/new`` and ``/{id}.png``.

    Routes
    ------
    ``POST {prefix}/new`` → ``{"id": str}``. The client then fetches the image.
    ``GET  {prefix}/{id}.png`` → PNG bytes (``image/png``).
    ``POST {prefix}/verify`` (form: ``id``, ``answer``) → ``{"ok": bool}``.
    """
    _tags: list[str | Enum] = [*(tags or ["captcha"])]
    router = APIRouter(prefix=prefix, tags=_tags)
    images: dict[str, bytes] = {}

    @router.post("/new")
    async def new_challenge() -> dict[str, str]:
        cid, png = await manager.issue()
        images[cid] = png
        return {"id": cid, "image_url": f"{prefix}/{cid}.png"}

    @router.get("/{challenge_id}.png")
    async def get_image(challenge_id: str) -> Response:
        png = images.pop(challenge_id, None)
        if png is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="not found")
        return Response(content=png, media_type=manager.renderer.content_type)

    @router.post("/verify")
    async def do_verify(
        challenge_id: Annotated[str, Form(alias="id")],
        answer: Annotated[str, Form()],
    ) -> dict[str, bool]:
        try:
            ok = await manager.verify(challenge_id, answer)
        except ChallengeNotFound as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="challenge not found"
            ) from exc
        except ChallengeExpired as exc:
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail="challenge expired"
            ) from exc
        except TooManyAttempts as exc:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many attempts",
            ) from exc
        return {"ok": ok}

    return router


def verify_captcha(
    manager: CaptchaManager,
) -> Callable[..., Coroutine[Any, Any, None]]:
    """Dependency that verifies a captcha submitted as form fields.

    Expected fields (``application/x-www-form-urlencoded`` or multipart):

    * ``captcha_id`` — id returned by ``POST /captcha/new``
    * ``captcha_answer`` — the user's answer

    On success, returns ``None`` so the wrapped route body runs. On failure,
    raises the appropriate :class:`HTTPException` (404 / 410 / 429 / 403).
    """

    async def _dep(
        captcha_id: Annotated[str, Form()],
        captcha_answer: Annotated[str, Form()],
    ) -> None:
        try:
            ok = await manager.verify(captcha_id, captcha_answer)
        except ChallengeNotFound as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="challenge not found"
            ) from exc
        except ChallengeExpired as exc:
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail="challenge expired"
            ) from exc
        except TooManyAttempts as exc:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="too many attempts",
            ) from exc
        if not ok:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="wrong answer")

    return _dep


__all__ = ["Depends", "captcha_router", "verify_captcha"]
