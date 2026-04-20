# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned for 0.3
- `discord.py` adapter (verification cog).
- `AudioChallenge` (optional, requires extra).
- `WordChallenge` (list-based accessibility challenge).
- `mkdocs-material` site published to GitHub Pages.

## [0.2.0] - 2026-04-20

### Added
- `RedisStorage`: async Redis-backed storage backend (`pip install "captchakit[redis]"`).
  Uses native Redis TTL via `SETEX` for automatic cleanup; multi-process safe.
- `EmojiGridChallengeFactory`: single-pick emoji-grid challenges. One target
  emoji is placed in a random cell of a grid of distractors; the expected
  answer is the 1-indexed cell number. Suitable for Telegram/Discord
  inline-button flows.
- `captchakit.adapters.aiogram.send_captcha`: helper that issues a challenge,
  uploads the rendered image via `bot.send_photo`, and returns the challenge
  id (`pip install "captchakit[aiogram]"`). Stays thin — user state is the
  caller's responsibility (typically aiogram FSM).
- Lazy `RedisStorage` re-export via `captchakit.storage.__getattr__`, so users
  who haven't installed the `redis` extra don't hit ImportError at
  `from captchakit.storage import ...`.

### Internal
- `fakeredis`, `aiogram`, `redis` added to `[dev]` extra to support CI tests.

## [0.1.0] - 2026-04-20

### Added
- Initial public release.
- Core `CaptchaManager` orchestrator with async `issue()` / `verify()` / `discard()` API.
- `TextChallengeFactory` (alphanumeric, visually-unambiguous charset by default).
- `MathChallengeFactory` (configurable operands / operators; non-negative results).
- `ImageRenderer` (Pillow, `asyncio.to_thread` offload, PNG output).
- `MemoryStorage` with attempt tracking and `cleanup_expired()`.
- FastAPI adapter: `captcha_router()` + `verify_captcha` dependency.
- Rich exception hierarchy (`CaptchaKitError` → `ChallengeError` →
  `ChallengeNotFound` / `ChallengeExpired` / `TooManyAttempts`).
- Full type hints (`py.typed`), mypy `--strict` clean.
- Constant-time answer comparison via `hmac.compare_digest`.
- Cryptographically secure solution generation via `secrets`.
- Example: FastAPI login form (HTML + endpoint).
- CI: lint (ruff) + type (mypy) + tests (pytest) on Python 3.10–3.13, 3 OSes.
- 36 tests, 98% branch coverage.
