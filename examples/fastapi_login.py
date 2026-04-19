"""Minimal FastAPI example — protect a form with pycaptcha.

Run::

    uv run python -m uvicorn examples.fastapi_login:app --reload

(Using ``python -m uvicorn`` guarantees the reloader's child process
reuses the project venv; ``uv run uvicorn`` may pick up a system-wide
``uvicorn`` that can't see the local package.)

Open http://127.0.0.1:8000 and submit the form.
"""

from __future__ import annotations

from fastapi import Depends, FastAPI
from fastapi.responses import HTMLResponse

from pycaptcha import (
    CaptchaManager,
    ImageRenderer,
    MathChallengeFactory,
    MemoryStorage,
)
from pycaptcha.adapters.fastapi import captcha_router, verify_captcha

manager = CaptchaManager(
    factory=MathChallengeFactory(),
    renderer=ImageRenderer(),
    storage=MemoryStorage(),
    ttl=120.0,
)

app = FastAPI(title="pycaptcha demo")
app.include_router(captcha_router(manager, prefix="/captcha"))


HTML = """
<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>pycaptcha demo</title></head>
<body style="font-family: sans-serif; max-width: 420px; margin: 40px auto;">
<h1>Prove you're human</h1>
<form id="f">
  <img id="img" alt="captcha" style="border:1px solid #ccc"/>
  <input type="hidden" name="captcha_id" id="cid"/>
  <p><input name="captcha_answer" autocomplete="off" required autofocus/></p>
  <button type="submit">Submit</button>
  <button type="button" id="refresh">New captcha</button>
</form>
<pre id="out"></pre>
<script>
async function load() {
  const r = await fetch('/captcha/new', {method:'POST'});
  const j = await r.json();
  document.getElementById('cid').value = j.id;
  document.getElementById('img').src = j.image_url + '?t=' + Date.now();
}
document.getElementById('refresh').onclick = load;
document.getElementById('f').onsubmit = async (e) => {
  e.preventDefault();
  const body = new FormData(e.target);
  const r = await fetch('/protected', {method:'POST', body});
  document.getElementById('out').textContent = r.status + ' ' + await r.text();
  if (r.status !== 200) load();
};
load();
</script>
</body></html>
"""


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return HTML


@app.post("/protected")
async def protected(_: None = Depends(verify_captcha(manager))) -> dict[str, str]:
    return {"message": "Welcome, human!"}
