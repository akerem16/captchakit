# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-04-20

First production-ready release. **No breaking changes from 0.5.0** —
all public imports keep working.

### Stabilised
- The full public surface listed in
  [docs/stability.md](https://akerem16.github.io/captchakit/stability/)
  is now covered by semver. Future `1.x` releases will only add or
  deprecate — never remove — public names.
- Classifier bumped to `Development Status :: 5 - Production/Stable`.

### Added
- `bandit` and `pip-audit` as CI gates; repo is clean against both
  at release time.
- `benchmarks/bench.py` — reproducible micro-benchmarks for every
  renderer and the issue → verify round-trip.
- `docs/stability.md` — formal versioning, deprecation window
  (2 MINOR) and supported-Python policy.

### Changed
- `README.md` rewritten for production audiences: architecture
  diagram, performance numbers, deployment checklist, security
  scope.
- `SECURITY.md` updated to reflect the `1.x` support matrix.

## [0.5.0] - 2026-04-20

### Added
- `PostgresStorage` (`pip install "captchakit[postgres]"`): asyncpg-backed
  storage with JSONB payload and `expires_at` index. Exposes
  `create_schema()` for idempotent table bootstrap and
  `cleanup_expired()` for periodic eviction. Lazy re-export via
  `captchakit.storage.__getattr__`.
- `SVGRenderer`: pure-Python vector renderer, no Pillow. Reuses
  `Theme` for colours and noise density. Content type
  `image/svg+xml`; ~10× smaller payload than the equivalent PNG.
- `RateLimiter` protocol with `NoOpRateLimiter` default and in-memory
  `TokenBucketRateLimiter`. Redis-backed `RedisTokenBucket` (atomic Lua
  script) via the existing `[redis]` extra.
  `CaptchaManager.issue(key=...)` optional parameter — passes the
  caller identity to the limiter. New `RateLimited` exception.
- Django adapter (`pip install "captchakit[django]"`): `CaptchaField`,
  `CaptchaWidget` and `captcha_image_view`. Bridges the async
  `CaptchaManager` via `asgiref.sync.async_to_sync`.

## [0.4.1] - 2026-04-20

### Fixed
- CI format check regression: `tests/test_theme.py` was committed without
  `ruff format`, blocking the 0.4.0 PyPI release. No runtime changes.

## [0.4.0] - 2026-04-20

### Added
- `AudioRenderer`: accessibility-oriented audio renderer. Encodes the
  challenge solution as a sequence of sine-wave tones (one per character)
  and returns a WAV byte-stream. Zero runtime deps — stdlib `wave` only.
- `Theme` with built-in presets: `Theme.CLASSIC`, `Theme.DARK`,
  `Theme.PASTEL`, `Theme.HIGH_CONTRAST` (WCAG-friendly). `ImageRenderer`
  now accepts a `theme=` keyword and exposes `bg_color`, `palette`,
  `noise_lines` via the theme.
- `PromptTranslator` protocol + `DefaultTranslator` with bundled
  English, Turkish, German and Spanish strings. `EmojiGridChallengeFactory`
  and `MathChallengeFactory` accept optional `translator=` and `locale=`.
- `MetricsSink` protocol with default `NoOpMetrics`. `CaptchaManager`
  emits one callback per lifecycle event (issue, verify success/fail,
  expiration, too-many-attempts).
- `PrometheusMetrics` adapter (`pip install "captchakit[metrics]"`).
  Exports `captchakit_issued_total`, `captchakit_verified_total`,
  `captchakit_expired_total`, `captchakit_too_many_attempts_total`.
- Documentation: four new pages (Themes, Audio, i18n, Metrics).

## [0.3.0] - 2026-04-20

### Added
- `discord.py` adapter: `captchakit.adapters.discord.send_captcha(channel, manager)`
  helper (`pip install "captchakit[discord]"`). Mirrors the aiogram adapter —
  thin, stateless, returns the challenge id for the caller to persist.
- `WordChallengeFactory`: accessibility-oriented factory that picks a real
  word from a bundled 50-word English list (or a user-supplied tuple).
- `mkdocs-material` documentation site: quickstart, adapter guides, storage
  guide, API reference via `mkdocstrings`. Deployed from `main` to
  `gh-pages` through `.github/workflows/docs.yml`.

### Changed
- `ROADMAP.md` rewritten as a concise English overview; detailed
  implementation plans were migrated into CHANGELOG / CONTRIBUTING /
  docs where they belong.

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
