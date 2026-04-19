# Contributing to pycaptcha

Thanks for your interest! Contributions of all kinds are welcome — bug reports,
feature requests, documentation fixes, new challenge types, new storage
backends, new framework adapters.

## Quick start

```bash
git clone https://github.com/akerem16/pycaptcha
cd pycaptcha
uv sync --all-extras
```

That's it — `uv` creates the virtualenv, installs every extra, and links the
package in editable mode.

## Running the checks

Every CI gate can be reproduced locally:

```bash
uv run ruff check .          # lint
uv run ruff format .         # auto-format
uv run mypy                  # strict type-check
uv run pytest                # run the test suite
uv run pytest --cov=pycaptcha --cov-report=term-missing
```

A pull request is merge-ready when all four pass and coverage stays ≥ 90%.

## Guidelines

### Scope
This library stays deliberately small. Before opening a large PR, please open
an issue first so we can agree on the direction. "Small" means:
- Core has **zero runtime deps beyond Pillow** — anything else is an extra.
- Every public API is async and fully type-hinted.
- Every public symbol is re-exported from `pycaptcha` and listed in `__all__`.

### Adding a challenge type
1. Subclass the `ChallengeFactory` protocol (see `challenges/text.py`).
2. Return a `ChallengeSpec(prompt, solution, case_sensitive=...)`.
3. Add tests covering happy path + validation errors.
4. Re-export from `pycaptcha/challenges/__init__.py` and the top-level
   `pycaptcha/__init__.py`.

### Adding a storage backend
1. Implement the `Storage` protocol (`storage/base.py`).
2. Make every operation async and concurrent-safe.
3. Place third-party client dependency under a new optional extra in
   `pyproject.toml`, not in core.
4. Mirror `MemoryStorage`'s test coverage.

### Adding a framework adapter
1. Create `src/pycaptcha/adapters/<framework>.py`.
2. Guard the framework import with a friendly error pointing at the extra.
3. Keep the adapter a **thin** translation layer — business logic stays in
   `CaptchaManager`.
4. Add adapter tests under `tests/` using the framework's own test utilities.

### Commit messages
No hard rule, but prefer [Conventional Commits](https://www.conventionalcommits.org/):

```
feat(storage): add RedisStorage
fix(manager): don't raise TooManyAttempts on the 3rd correct answer
docs(readme): add FastAPI demo instructions
```

## Reporting security issues
Please **do not** open a public issue. See [SECURITY.md](SECURITY.md).
