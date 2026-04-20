"""Prompt translation hooks.

Challenge factories produce short fragments of text that are shown to
the user (e.g. ``"Which cell contains 🍎?"``). To localise them, pass a
:class:`PromptTranslator` to the factory.

Built-in keys
-------------
- ``grid.pick`` with params ``emoji`` — used by
  :class:`EmojiGridChallengeFactory`. The default English text is
  ``"Which cell contains {emoji}? Reply with the number."``.
- ``math.ask`` with params ``a``, ``op``, ``b`` — optional key that
  :class:`MathChallengeFactory` will use if a translator is supplied.

Other factories (``Text``, ``Word``) emit the raw solution as the
prompt and don't need translation.

The :class:`DefaultTranslator` ships fallbacks for ``en``, ``tr``,
``de`` and ``es``; unknown locales fall back to ``en``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class PromptTranslator(Protocol):
    """Maps ``(key, locale, **params)`` → a rendered string."""

    def translate(self, key: str, locale: str, /, **params: Any) -> str: ...


_BUILTIN_CATALOG: dict[str, dict[str, str]] = {
    "en": {
        "grid.pick": "Which cell contains {emoji}? Reply with the number.",
        "math.ask": "{a} {op} {b} = ?",
    },
    "tr": {
        "grid.pick": "Hangi hücrede {emoji} var? Sayı ile cevapla.",  # noqa: RUF001
        "math.ask": "{a} {op} {b} = ?",
    },
    "de": {
        "grid.pick": "Welche Zelle enthält {emoji}? Antworte mit der Zahl.",
        "math.ask": "{a} {op} {b} = ?",
    },
    "es": {
        "grid.pick": "¿Qué celda contiene {emoji}? Responde con el número.",
        "math.ask": "{a} {op} {b} = ?",
    },
}


@dataclass(slots=True)
class DefaultTranslator:
    """In-memory translator with English, Turkish, German and Spanish.

    Pass ``catalog`` to override or extend the bundled strings::

        translator = DefaultTranslator(
            catalog={"fr": {"grid.pick": "Quelle case contient {emoji} ?"}},
        )

    Keys missing in the requested locale fall back to ``default_locale``
    ("en"); keys missing everywhere raise :class:`KeyError`.
    """

    catalog: dict[str, dict[str, str]] = field(
        default_factory=lambda: {loc: dict(entries) for loc, entries in _BUILTIN_CATALOG.items()}
    )
    default_locale: str = "en"

    def translate(self, key: str, locale: str, /, **params: Any) -> str:
        table = self.catalog.get(locale) or self.catalog.get(self.default_locale) or {}
        template = table.get(key)
        if template is None:
            fallback = self.catalog.get(self.default_locale, {})
            template = fallback.get(key)
        if template is None:
            raise KeyError(f"no translation for key {key!r} in locale {locale!r}")
        return template.format(**params)


__all__ = ["DefaultTranslator", "PromptTranslator"]
