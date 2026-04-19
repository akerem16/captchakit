# captchakit — Geliştirme Yol Haritası

> Async-first, fully type-hinted, Pillow dışında runtime bağımlılığı olmayan, aiogram / FastAPI / Discord için hazır adapter'lı minimal captcha kütüphanesi.

**Python desteği:** 3.10+ (kullanıcı kararı; `match/case`, `X | Y` union, `ParamSpec`, `dataclass(slots=True)` kullanılabilir)
**Lisans:** MIT
**Hedef kitle:** Telegram/Discord bot geliştiricileri, FastAPI backend yazarları, küçük-orta ölçekli self-hosted servisler.

---

## 1. Vizyon & Konumlandırma

### 1.1 Problem
Python ekosisteminde captcha üreten kütüphaneler mevcut (lepture/captcha, claptcha, multicolorcaptcha, easy-captcha), fakat hepsinde şu boşluklar var:

| Eksik | Mevcut kütüphaneler | captchakit'nın tutumu |
|---|---|---|
| Async API | yok (hepsi sync) | `async def generate(...)`, thread-pool'a offload |
| `py.typed` + tam type hint | kısmi / yok | PEP 561 uyumlu, mypy strict'te geçer |
| Framework adapter | yok | aiogram, FastAPI, Discord (py-cord/discord.py) |
| Storage soyutlaması (challenge ↔ solution eşleme + TTL) | yok | `Protocol` tabanlı `Storage`; in-memory + Redis |
| Challenge çeşitliliği | genelde sadece text | text, math, emoji-grid, audio (opsiyonel ekstra) |
| Modern toolchain | setup.py, flake8 | uv + Ruff + mypy + hatchling |

### 1.2 Konum
**"Use-case odaklı bir captcha SDK"** — sadece görüntü üretmiyor; "kullanıcıya soru sor, cevabı doğrula, TTL ile temizle" akışını başından sonuna çözüyor. Web servisleri ve botlar için "drop-in" olacak.

### 1.3 Non-goals (netleşsin ki scope creep olmasın)
- Bot-solver / bypass aracı değil (2captcha, capsolver gibi).
- Production-grade CV-dirençli güvenlik captcha'sı değil. hCaptcha/reCAPTCHA'nın yerine geçmez; "basit human-check" katmanıdır. README'de açıkça yazılacak.
- ML / audio üretimi v1 için opsiyonel extra; core'un dışında.

---

## 2. Rakip Analizi (özet)

- **lepture/captcha** (v0.7.1, Mart 2025): En yaygın. Sync, `ImageCaptcha` + `AudioCaptcha`. Type hint kısmi, adapter yok.
- **claptcha**: Basit, Pillow tabanlı, bakım azalmış.
- **multicolorcaptcha**: Telegram bot odaklı math captcha, ama sync ve type hint yok.
- **fast_captcha**: FastAPI örneği, storage/TTL yönetimi yok.
- **TLG_JoinCaptchaBot / discordpy-captcha**: Kütüphane değil, uygulama.

**Fark yaratacağımız 3 şey:** (1) async-first + tam typed, (2) storage/expiry yönetimi core'da, (3) framework adapter'ları.

---

## 3. Teknik Gereksinimler

### 3.1 Runtime
- **Zorunlu:** `Pillow>=10.0`
- **Hiçbir başka runtime dep yok** (kararlılık ve "minimal" vaadi için).
- **Opsiyonel extras** (pyproject `[project.optional-dependencies]`):
  - `aiogram`: `aiogram>=3.4`
  - `fastapi`: `fastapi>=0.110`, `starlette`
  - `discord`: `discord.py>=2.3` (py-cord çatışmamak için tek seçim; adapter'ı soyutla)
  - `redis`: `redis>=5.0` (async client)
  - `audio`: opsiyonel; v0.3+ hedefi
  - `dev`: ruff, mypy, pytest, pytest-asyncio, hypothesis, coverage, mkdocs-material

### 3.2 Geliştirme toolchain'i
- **uv** — paket + venv
- **Ruff** — lint + format (black+isort+flake8 yerine)
- **mypy --strict** — tip kontrol
- **pytest + pytest-asyncio + hypothesis** — test
- **hatchling** — build backend
- **pre-commit** — hooks (ruff, mypy, trailing whitespace)
- **GitHub Actions** — CI matrisi

### 3.3 Desteklenen Python sürümleri
3.10, 3.11, 3.12, 3.13 — CI matrisinde hepsi.

---

## 4. Repo & Paket Yapısı

```
captchakit/
├── pyproject.toml
├── README.md                 # hook + quickstart + badges
├── ROADMAP.md                # (bu dosya)
├── CHANGELOG.md              # Keep a Changelog formatı
├── LICENSE                   # MIT
├── .github/
│   ├── workflows/ci.yml      # lint, type, test matrix
│   ├── workflows/release.yml # tag push -> PyPI trusted publishing
│   ├── ISSUE_TEMPLATE/
│   └── dependabot.yml
├── src/
│   └── captchakit/
│       ├── __init__.py       # public API re-exports
│       ├── py.typed          # PEP 561 işaretçisi
│       ├── types.py          # TypedDict, Protocol, TypeAlias
│       ├── challenges/
│       │   ├── base.py       # Challenge, Renderer protocolleri
│       │   ├── text.py       # TextChallenge
│       │   ├── math.py       # MathChallenge (2+3=?)
│       │   └── grid.py       # EmojiGridChallenge
│       ├── renderers/
│       │   ├── image.py      # Pillow renderer
│       │   └── fonts/        # DejaVu Sans (bundled, SIL OFL)
│       ├── storage/
│       │   ├── base.py       # Storage Protocol
│       │   ├── memory.py     # dict + asyncio.Lock
│       │   └── redis.py      # opsiyonel extra
│       ├── manager.py        # CaptchaManager (core orchestrator)
│       ├── errors.py         # custom exceptions
│       └── adapters/
│           ├── __init__.py
│           ├── aiogram.py    # middleware + helper
│           ├── fastapi.py    # dependency + router
│           └── discord.py    # cog + verification flow
├── tests/
│   ├── conftest.py
│   ├── test_manager.py
│   ├── test_challenges/
│   ├── test_renderers/
│   ├── test_storage/
│   └── adapters/
│       ├── test_aiogram.py
│       ├── test_fastapi.py
│       └── test_discord.py
├── examples/
│   ├── aiogram_bot.py
│   ├── fastapi_login.py
│   └── discord_verify.py
└── docs/                     # mkdocs-material
    ├── index.md
    ├── quickstart.md
    ├── adapters/
    └── api/
```

### 4.1 İsim kararı
- Dizin: `captchakit/` (GitHub repo adı da aynı).
- **Import adı da `captchakit`** (kullanıcı net şekilde aradığı için kısa olan tercih edildi).
- **PyPI'de `captchakit` müsaitliği kontrol edilmeli** (0.1 yayın öncesi). Alınmışsa alternatif: `captchakit` veya `captchakit-async`.

---

## 5. Mimari Kararlar

### 5.1 Katmanlar
```
┌─────────────────────────────────────────────────┐
│  Adapters (aiogram / fastapi / discord)         │ <- opsiyonel extras
├─────────────────────────────────────────────────┤
│  CaptchaManager  (public facade)                │
├──────────────┬──────────────┬───────────────────┤
│  Challenge   │  Renderer    │  Storage          │ <- Protocol'ler
│  (Text/Math) │  (Image)     │  (Memory/Redis)   │
└──────────────┴──────────────┴───────────────────┘
```

### 5.2 Temel tasarım prensipleri
- **Protocol > ABC:** structural typing ile dışarıdan implement edilebilsin.
- **Async pure:** CPU-bound Pillow işleri `asyncio.to_thread` ile offload.
- **Immutable challenge objects:** `@dataclass(frozen=True, slots=True)`.
- **Zamanı enjekte et:** `Clock` protocol'ü (test edilebilirlik). Varsayılan `time.monotonic`.
- **Kriptografik güvenli random:** `secrets.choice` (solution üretiminde). `random` kullanma.
- **Timing-safe comparison:** `hmac.compare_digest` çözüm doğrulamada.

### 5.3 Hataların hiyerarşisi
```python
class CaptchaKitError(Exception): ...
class ChallengeExpired(CaptchaKitError): ...
class ChallengeNotFound(CaptchaKitError): ...
class InvalidSolution(CaptchaKitError): ...
class TooManyAttempts(CaptchaKitError): ...
class StorageError(CaptchaKitError): ...
```

---

## 6. Core API (taslak)

### 6.1 Challenge & Renderer protocol'leri
```python
# challenges/base.py
from typing import Protocol, runtime_checkable
from dataclasses import dataclass

@dataclass(frozen=True, slots=True)
class Challenge:
    id: str                 # uuid4
    prompt: str             # "7 + 3 = ?" veya rastgele string
    solution: str           # karşılaştırma için (storage'a sadece hash'i gider)
    created_at: float
    expires_at: float
    max_attempts: int = 3

@runtime_checkable
class ChallengeFactory(Protocol):
    async def create(self) -> Challenge: ...

@runtime_checkable
class Renderer(Protocol):
    async def render(self, challenge: Challenge) -> bytes: ...  # PNG bytes
    content_type: str  # "image/png"
```

### 6.2 Storage protocol'ü
```python
# storage/base.py
class Storage(Protocol):
    async def put(self, challenge: Challenge) -> None: ...
    async def get(self, challenge_id: str) -> Challenge | None: ...
    async def delete(self, challenge_id: str) -> None: ...
    async def incr_attempts(self, challenge_id: str) -> int: ...
```

### 6.3 CaptchaManager (facade)
```python
class CaptchaManager:
    def __init__(
        self,
        factory: ChallengeFactory,
        renderer: Renderer,
        storage: Storage,
        *,
        ttl: float = 120.0,
        max_attempts: int = 3,
    ) -> None: ...

    async def issue(self) -> tuple[str, bytes]:
        """Yeni challenge üretir; (id, image_bytes) döner."""

    async def verify(self, challenge_id: str, user_input: str) -> bool:
        """Timing-safe karşılaştırma; başarılıysa storage'dan siler."""

    async def cleanup_expired(self) -> int:
        """Background task için; süresi geçenleri siler, sayısını döner."""
```

### 6.4 Public import yüzeyi
```python
# captchakit/__init__.py
from .manager import CaptchaManager
from .challenges import TextChallenge, MathChallenge
from .renderers import ImageRenderer
from .storage import MemoryStorage
from .errors import (
    CaptchaKitError, ChallengeExpired, ChallengeNotFound,
    InvalidSolution, TooManyAttempts,
)
__all__ = [...]
__version__ = "0.1.0"
```

---

## 7. Challenge Tipleri (sürüm planı)

| Tip | Örnek | Zorluk | Sürüm |
|---|---|---|---|
| `TextChallenge` | "h8k2x" (case-insensitive) | Temel | v0.1 |
| `MathChallenge` | "7 + 3 = ?" | Kolay, bot-spam önleme | v0.1 |
| `EmojiGridChallenge` | "🍎 olanları seç" (3×3) | Telegram/Discord inline button uyumlu | v0.2 |
| `WordChallenge` | "Sabit kelime listesinden 1 kelimeyi yaz" | Erişilebilirlik için | v0.2 |
| `AudioChallenge` | WAV (sayıları oku) | A11y | v0.3 (opsiyonel extra) |

---

## 8. Storage Backend'leri

- **`MemoryStorage`** (v0.1): `dict[str, Challenge]` + `asyncio.Lock`, periyodik `cleanup_expired` task'i.
- **`RedisStorage`** (v0.2, `extras=[redis]`): `SETEX` ile native TTL, `HINCRBY` ile attempt sayacı.
- **Kullanıcı kendi storage'ını yazabilir** (Protocol yüzünden).

---

## 9. Framework Adapter'ları

### 9.1 aiogram v3
```python
from captchakit.adapters.aiogram import CaptchaMiddleware

dp.chat_join_request.middleware(CaptchaMiddleware(manager=cm, ttl=120))
```
- `ChatJoinRequest` için otomatik captcha gönderimi (photo + InlineKeyboard veya reply text).
- Helper: `await send_captcha(bot, chat_id, manager)`.

### 9.2 FastAPI
```python
from captchakit.adapters.fastapi import captcha_router, get_captcha

app.include_router(captcha_router(manager=cm, prefix="/captcha"))
# GET  /captcha/new   -> {"id": "...", "image_url": "/captcha/{id}.png"}
# POST /captcha/verify {"id": ..., "answer": ...}

@app.post("/register")
async def register(_: None = Depends(get_captcha(cm))): ...
```
- Dependency `get_captcha(manager, form_field="captcha_id", answer_field="captcha_answer")`.

### 9.3 Discord (discord.py 2.x)
```python
from captchakit.adapters.discord import VerificationCog
bot.add_cog(VerificationCog(manager=cm, role_on_success="Verified"))
```
- `on_member_join` → DM ile captcha görseli gönder, cevap verene rol ata.
- Timeout → kick opsiyonu.

---

## 10. Test Stratejisi

- **Unit:** her challenge/renderer/storage bağımsız test (≥%90 coverage).
- **Property-based (hypothesis):** solution length/charset invariant'ları, TTL monotonluğu.
- **Integration:** `CaptchaManager.issue → verify` golden path + 5 hata yolu (expired, not found, wrong, attempts exhausted, storage error).
- **Visual regression:** `tests/fixtures/` altında referans PNG; pixel diff toleransı (font rendering platformlar arası farkı var — CI image'ı sabitle).
- **Adapter testleri:**
  - aiogram: `aiogram.test_utils` / mock bot + fake update.
  - FastAPI: `TestClient` / `httpx.AsyncClient`.
  - Discord: mock'lu birim test (gerçek gateway'e bağlanma).
- **Redis:** `fakeredis[asyncio]` ile.

---

## 11. CI / CD

`.github/workflows/ci.yml`:
- Matrix: `{os: [ubuntu, windows, macos], python: [3.10, 3.11, 3.12, 3.13]}`
- Adımlar: `uv sync` → `ruff check` → `ruff format --check` → `mypy --strict` → `pytest --cov` → `codecov upload` (opsiyonel)

`release.yml`:
- `v*` tag push → hatch build → **PyPI Trusted Publishing** (OIDC, token'sız)
- GitHub Release otomatik changelog ile (`release-drafter` veya manuel).

---

## 12. Dokümantasyon

- **mkdocs-material** + `mkdocstrings` (autogen API ref).
- İçerik:
  1. `index.md` — vaat, 10 satırlık quickstart
  2. `quickstart.md` — memory + FastAPI ile ilk captcha
  3. `challenges.md` — tipler, özelleştirme
  4. `storage.md` — memory vs redis, kendi storage'ını yaz
  5. `adapters/aiogram.md`, `fastapi.md`, `discord.md`
  6. `security.md` — *"Bu kütüphane botnet-grade captcha değildir; neden?"* + önerilen yanlarda rate limiting
  7. `api/` — mkdocstrings autogen
- **GitHub Pages'e deploy** (release workflow'unda).

---

## 13. Sürüm Yol Haritası

| Sürüm | İçerik | Tahmin |
|---|---|---|
| **v0.1.0** (MVP) | Core Manager, TextChallenge, MathChallenge, ImageRenderer, MemoryStorage, FastAPI adapter, README + quickstart | 1–2 hafta (akşam çalışmasıyla) |
| **v0.2.0** | aiogram adapter, RedisStorage, EmojiGridChallenge, mkdocs site yayın | +1 hafta |
| **v0.3.0** | Discord adapter, AudioChallenge (opsiyonel), WordChallenge | +1 hafta |
| **v0.4.0** | i18n (prompt çevirileri), özelleştirilebilir tema (renk/font preset), metrics hook (Prometheus-compatible callback) | +1 hafta |
| **v1.0.0** | API stabil, semver taahhüdü, tüm adapter'lar için ≥%90 coverage, ayrıntılı güvenlik dokümanı, CHANGELOG düzeni | Önceki adımlar sonrası |

### Her sürümde "Definition of Done"
- `mypy --strict` temiz
- `ruff check` temiz
- Coverage ≥ %90
- CHANGELOG güncel
- Yeni özellik için en az bir `examples/` örneği
- README badge'leri yeşil

---

## 14. GitHub Profil Etkisi (senin hedefin)

Bu kadar plan niye? Çünkü açık kaynak bir projeyi "yapıp attın mı profile güzel görünsün" bakışıyla değil, küçük ama **özenli** bir SDK gibi kurarsan:
- Tam typed + `py.typed` → recruiter'lar için "bu adam paketleme biliyor" sinyali.
- Framework adapter'ları → gerçek kullanım senaryosu, sadece toy değil.
- Test coverage badge + mypy strict badge + PyPI badge → README'de üç satır güven.
- mkdocs sitesi → dokümantasyon yazabildiğini gösterir (çok nadir).
- "Awesome-python" / "awesome-aiogram" PR'ı ile referans alma şansı yüksek.

Sürüm kesmeden *önce* yapılacaklar:
- [ ] Repo açılışında **iyi bir README** (vaat + karşılaştırma tablosu + 10-satırlık örnek)
- [ ] Sosyal preview image (GitHub repo settings)
- [ ] `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`
- [ ] İlk release'te r/Python + dev.to duyurusu

---

## 15. Riskler & Açık Sorular

| Risk | Etki | Azaltma |
|---|---|---|
| PyPI'de `captchakit` alınmış olabilir | Orta | Yayın öncesi kontrol, yedek ad: `captchakit` |
| Font rendering platform farkları → pixel diff testleri flaky | Düşük | Bundled tek font (DejaVu Sans OFL), CI image'ı sabit |
| Pillow ABI kırılmaları (her yıl) | Orta | CI'de Pillow son 2 major + güncel; `Pillow>=10,<12` pin |
| Discord.py vs py-cord çatallanması | Orta | Extra adını `discord` yerine `discordpy` yap, py-cord için ayrı extra |
| aiogram 3.x breaking API'ler (3.4→3.x) | Orta | CI'de aiogram son 2 minor, changelog izle |
| "Basit captcha güvenli değil" eleştirisi | Düşük | Dokümanda açıkça sınırı anlat; hCaptcha/Turnstile önerisi ekle |

### Açık sorular (sürüm öncesi cevaplanmalı)
1. Adapter'lar aynı pakette mi, ayrı paketler mi? → **Aynı pakette + extras** (tek repo, kolay bakım). Değişebilir.
2. `audio` için `pydub`/`numpy` zorunlu olur, "zero-dep" vaadiyle çatışır → opsiyonel extra + dok notu.
3. v1.0'dan sonra deprecation politikası: en az 1 minor önceden uyarı.

---

## 16. İlk Hafta Mikro Plan (yarın başlarsan)

**Gün 1:** `pyproject.toml`, `src/captchakit/__init__.py`, `py.typed`, `ruff + mypy + pytest` kurulum, CI iskeleti.
**Gün 2:** `errors.py`, `types.py`, `challenges/base.py`, `TextChallenge`.
**Gün 3:** `renderers/image.py` (Pillow) + `tests/test_renderers`.
**Gün 4:** `storage/memory.py` + `manager.py` + uçtan uca test.
**Gün 5:** FastAPI adapter + `examples/fastapi_login.py`.
**Gün 6:** README yaz, badge'leri ekle, mkdocs iskeleti.
**Gün 7:** PyPI kontrol → `v0.1.0-rc1` → feedback → `v0.1.0`.

---

## Kaynaklar

- lepture/captcha: <https://github.com/lepture/captcha>
- claptcha: <https://github.com/kuszaj/claptcha>
- multicolorcaptcha: <https://github.com/J-Rios/multicolorcaptcha>
- aiogram 3.x: <https://github.com/aiogram/aiogram>
- FastAPI best practices 2026: <https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026>
- Python packaging 2026 (uv + ruff + mypy): <https://www.kdnuggets.com/python-project-setup-2026-uv-ruff-ty-polars>
- PEP 561 (py.typed): <https://peps.python.org/pep-0561/>
- PyPI Trusted Publishing: <https://docs.pypi.org/trusted-publishers/>
