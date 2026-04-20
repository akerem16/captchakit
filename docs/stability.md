# Stability & versioning

`captchakit` follows [Semantic Versioning 2.0](https://semver.org/) as
of **v1.0.0**. This page documents what that means in practice.

## What counts as public API

Anything importable from the top-level package:

```python
from captchakit import ...                       # public
from captchakit.adapters.fastapi import ...      # public
from captchakit.adapters.aiogram import ...      # public
from captchakit.adapters.discord import ...      # public
from captchakit.adapters.django import ...       # public
from captchakit.storage import ...               # public
from captchakit.renderers import ...             # public
from captchakit.challenges import ...            # public
from captchakit.metrics import ...               # public
from captchakit.metrics_prometheus import ...    # public
from captchakit.ratelimit import ...             # public
from captchakit.ratelimit_redis import ...       # public
from captchakit.i18n import ...                  # public
```

Also stable:

- The wire format of stored `Challenge` JSON in `RedisStorage` and
  `PostgresStorage` (forwards-compatible: new fields may be added with
  defaults; removal is a breaking change).
- The shape of the `MetricsSink` callbacks — new callbacks may be added
  in minor releases, existing callbacks won't change signatures.
- The default parameter values on all dataclasses (changes bumped as
  MINOR to alert operators, deprecation first).

## What is NOT public

- Anything prefixed with `_` (`_clock`, internal helpers).
- The exact bytes produced by `ImageRenderer` / `SVGRenderer` —
  rendering is randomised and the visual output may be tweaked in
  PATCH releases for legibility or performance.
- Private methods on dataclasses, even when technically accessible.
- Internal tests and fixtures.

## Deprecation policy

Anything we intend to remove follows a **two-minor-version window**:

1. **Minor N** — deprecation warning emitted (`DeprecationWarning`)
   and a clear alternative documented in CHANGELOG.
2. **Minor N+2** — removal. Never earlier.

If we need to fix a security issue by removing something, we'll say so
explicitly in the CHANGELOG and document the workaround — but we will
always ship a PATCH release first that allows coexistence when feasible.

## Supported Python versions

We test against every CPython version that is still within its upstream
support window. The current matrix:

| Python | Status        |
| ------ | ------------- |
| 3.10   | supported     |
| 3.11   | supported     |
| 3.12   | supported     |
| 3.13   | supported     |

When a Python minor goes end-of-life upstream, we drop it **at the next
MINOR release** (not PATCH), with a row in CHANGELOG explaining when
support ends.

## Security fixes

- Every actively supported MINOR line of `1.x` receives security
  patches.
- Non-security bug fixes go to the latest MINOR only; if you need a
  back-port, open an issue.

Reporting a vulnerability: see [SECURITY.md](https://github.com/akerem16/captchakit/blob/main/SECURITY.md).
