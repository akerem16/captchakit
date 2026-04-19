from __future__ import annotations

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("httpx")

from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from captchakit import (
    CaptchaManager,
    ImageRenderer,
    MemoryStorage,
    TextChallengeFactory,
)
from captchakit.adapters.fastapi import captcha_router, verify_captcha


def _make_app() -> tuple[FastAPI, CaptchaManager]:
    manager = CaptchaManager(
        factory=TextChallengeFactory(length=4),
        renderer=ImageRenderer(width=120, height=60, font_size=24),
        storage=MemoryStorage(),
        ttl=60.0,
    )
    app = FastAPI()
    app.include_router(captcha_router(manager, prefix="/captcha"))

    @app.post("/protected")
    async def protected(_: None = Depends(verify_captcha(manager))) -> dict[str, bool]:
        return {"ok": True}

    return app, manager


async def test_new_and_image_roundtrip() -> None:
    app, _ = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/captcha/new")
        assert r.status_code == 200
        body = r.json()
        assert "id" in body and "image_url" in body
        img = await c.get(body["image_url"])
        assert img.status_code == 200
        assert img.headers["content-type"].startswith("image/png")
        assert img.content.startswith(b"\x89PNG")


async def test_verify_route_ok_and_wrong() -> None:
    app, manager = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/captcha/new")
        cid = r.json()["id"]
        ch = await manager.storage.get(cid)
        assert ch is not None

        wrong = await c.post("/captcha/verify", data={"id": cid, "answer": "zzzz"})
        assert wrong.status_code == 200
        assert wrong.json() == {"ok": False}

        ok = await c.post("/captcha/verify", data={"id": cid, "answer": ch.solution})
        assert ok.status_code == 200
        assert ok.json() == {"ok": True}


async def test_protected_route_requires_correct_answer() -> None:
    app, manager = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/captcha/new")
        cid = r.json()["id"]
        ch = await manager.storage.get(cid)
        assert ch is not None

        fail = await c.post(
            "/protected",
            data={"captcha_id": cid, "captcha_answer": "xxxx"},
        )
        assert fail.status_code == 403

        ok = await c.post(
            "/protected",
            data={"captcha_id": cid, "captcha_answer": ch.solution},
        )
        assert ok.status_code == 200
        assert ok.json() == {"ok": True}


async def test_verify_missing_returns_404() -> None:
    app, _ = _make_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        r = await c.post("/captcha/verify", data={"id": "nope", "answer": "x"})
        assert r.status_code == 404
