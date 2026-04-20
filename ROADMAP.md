# captchakit — Roadmap

> Async-first, fully type-hinted, minimal captcha library with framework
> adapters.

**Python:** 3.10+ · **License:** MIT · **Audience:** Telegram / Discord bot
developers, FastAPI backend authors, small-to-mid self-hosted services that
want a lightweight human-check without pulling in a third-party service.

---

## Vision

Most Python captcha libraries are sync, partially typed, and stop at "render
a PNG." They leave TTL, attempt tracking, storage, and framework integration
as homework. captchakit closes that gap: a small, modern SDK you drop into
an async codebase and forget about.

## Pillars

1. **Async-first.** Every public API is awaitable; CPU-bound Pillow work is
   offloaded so the event loop never blocks.
2. **Fully typed.** `py.typed` marker + `mypy --strict` clean. IDEs get real
   autocompletion.
3. **Minimal core.** One runtime dependency: Pillow. Everything else —
   Redis, aiogram, FastAPI, discord.py — is an opt-in extra.
4. **Pluggable.** Challenges, renderers and storage are `Protocol`-based, so
   you can swap any layer without subclassing.
5. **Safe defaults.** Crypto-safe randomness (`secrets`), constant-time
   comparison (`hmac.compare_digest`), TTL + attempt limits enforced by the
   manager.

## Non-goals

- Not a CAPTCHA-solving bot framework. captchakit generates challenges; it
  does not bypass hCaptcha / reCAPTCHA / Turnstile.
- Not a defence against modern OCR or solver farms. For high-value surfaces
  (login, payment, password reset), use a purpose-built service in addition.
- Not an orchestration framework. Adapters stay thin; user/session state
  belongs to the host application (FSM, cookies, session store).

## Version roadmap

| Version | Status | Scope |
|---|---|---|
| **0.1** | ✅ released | Core `CaptchaManager` · Text / Math challenges · Image renderer · Memory storage · FastAPI adapter |
| **0.2** | ✅ released | `RedisStorage` · `EmojiGridChallenge` · aiogram adapter |
| **0.3** | in progress | `discord.py` adapter · `WordChallenge` · docs site |
| **0.4** | planned | `AudioChallenge` (optional extra) · i18n hooks · theming presets · metrics callbacks |
| **1.0** | planned | Stable API, semver commitment, ≥90% coverage on every adapter, hardened security docs |

Each release keeps the gate: `ruff` + `mypy --strict` + `pytest` green, coverage
≥ 90%, CHANGELOG entry, one runnable example.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup, adding a challenge /
storage / adapter, and the commit-message convention.

## Security

See [SECURITY.md](SECURITY.md) for the threat model and vulnerability
reporting channel.
