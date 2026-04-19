# Security Policy

## Supported versions

| Version | Supported |
|---|---|
| 0.1.x | ✅ |
| < 0.1 | ❌ |

During 0.x the API is allowed to evolve; security fixes are backported to the
most recent minor release only.

## Reporting a vulnerability

If you believe you've found a security issue in pycaptcha, please **do not**
open a public GitHub issue. Instead, email **akerembegic16@gmail.com** with:

- a short description of the issue,
- steps to reproduce (or a proof-of-concept), and
- the affected version(s).

You'll get an acknowledgement within 72 hours. If the issue is confirmed I'll
work with you on a fix and a coordinated disclosure timeline (typically 30
days from confirmation).

## Threat model — what pycaptcha is and isn't

pycaptcha is a **lightweight human-check** intended to raise the cost of
casual / scripted spam in use cases such as:

- Telegram / Discord join-verification
- low-value FastAPI sign-up or contact forms
- internal tools

It is **not** a defence against a determined attacker using modern OCR or a
human-solver farm. For high-value surfaces (login, payment, password reset)
use a purpose-built service such as **hCaptcha**, **Cloudflare Turnstile**,
or **reCAPTCHA Enterprise**, ideally in addition to pycaptcha.

### What the library does guarantee

- **Constant-time answer comparison** (`hmac.compare_digest`) — timing side
  channels on the verification path are mitigated.
- **Cryptographically secure solution generation** (`secrets.choice`,
  `secrets.randbelow`) — solutions are not predictable from prior outputs.
- **TTL + attempt limits** enforced by `CaptchaManager` — a stolen challenge
  id has a bounded lifetime and a bounded number of guesses.
- **No solution logging by default** — solutions live only in the selected
  storage backend and are evicted on success, failure-with-attempts-exhausted,
  or TTL expiry.

### What the library does not defend against

- **Automated OCR** — the built-in `ImageRenderer` is not OCR-resistant.
  It's a visual check, not a CV-hardened one.
- **Replay of the image to a solver farm** — any third-party solver that can
  read the prompt can answer correctly. Combine with rate limiting.
- **Shared state across processes** in `MemoryStorage` — use `RedisStorage`
  (coming in 0.2) or another shared backend for multi-worker deployments.
- **Challenge-id enumeration** — ids are UUID4 (122 bits of randomness) so
  guessing is infeasible, but if your application leaks ids (e.g. in logs or
  URLs) an attacker can try to solve them directly.

## Dependencies

Core runtime dependencies are deliberately minimal: **Pillow only**. Every
framework adapter and storage backend lives behind an optional extra, so you
can audit exactly what your deployment pulls in.
