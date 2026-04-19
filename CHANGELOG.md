# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for 0.2
- `aiogram` adapter (middleware + helper for chat-join verification).
- `RedisStorage` backend (async, native TTL via `SETEX`).
- `EmojiGridChallenge`.
- `mkdocs-material` site published to GitHub Pages.

## [0.1.0] - 2026-04-20

### Added
- Initial public release.
- Core `CaptchaManager` orchestrator with async `issue()` / `verify()` / `discard()` API.
- `TextChallengeFactory` (alphanumeric, visually-unambiguous charset by default).
- `MathChallengeFactory` (configurable operands / operators; non-negative results).
- `ImageRenderer` (Pillow, `asyncio.to_thread` offload, PNG output).
- `MemoryStorage` with attempt tracking and `cleanup_expired()`.
- FastAPI adapter: `captcha_router()` + `verify_captcha` dependency.
- Rich exception hierarchy (`PyCaptchaError` → `ChallengeError` →
  `ChallengeNotFound` / `ChallengeExpired` / `TooManyAttempts`).
- Full type hints (`py.typed`), mypy `--strict` clean.
- Constant-time answer comparison via `hmac.compare_digest`.
- Cryptographically secure solution generation via `secrets`.
- Example: FastAPI login form (HTML + endpoint).
- CI: lint (ruff) + type (mypy) + tests (pytest) on Python 3.10–3.13, 3 OSes.
- 36 tests, 98% branch coverage.
