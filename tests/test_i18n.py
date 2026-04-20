from __future__ import annotations

import pytest

from captchakit import (
    DefaultTranslator,
    EmojiGridChallengeFactory,
    MathChallengeFactory,
    PromptTranslator,
)


def test_default_translator_implements_protocol() -> None:
    assert isinstance(DefaultTranslator(), PromptTranslator)


def test_default_translator_has_bundled_locales() -> None:
    t = DefaultTranslator()
    assert "Hangi" in t.translate("grid.pick", "tr", emoji="🍎")
    assert "Welche" in t.translate("grid.pick", "de", emoji="🍎")
    assert "celda" in t.translate("grid.pick", "es", emoji="🍎")


def test_unknown_locale_falls_back_to_default() -> None:
    t = DefaultTranslator()
    out = t.translate("grid.pick", "ja", emoji="🍎")
    assert "cell" in out.lower()


def test_unknown_key_raises() -> None:
    t = DefaultTranslator()
    with pytest.raises(KeyError):
        t.translate("does.not.exist", "en")


def test_catalog_override() -> None:
    t = DefaultTranslator(catalog={"fr": {"grid.pick": "Quelle case contient {emoji} ?"}})
    assert t.translate("grid.pick", "fr", emoji="🍎") == "Quelle case contient 🍎 ?"


async def test_grid_factory_uses_translator() -> None:
    translator = DefaultTranslator()
    factory = EmojiGridChallengeFactory(size=4, translator=translator, locale="tr")
    spec = await factory.create()
    assert "Hangi" in spec.prompt


async def test_grid_factory_default_is_english() -> None:
    factory = EmojiGridChallengeFactory(size=4)
    spec = await factory.create()
    assert "Which cell" in spec.prompt


async def test_math_factory_uses_translator() -> None:
    translator = DefaultTranslator()
    factory = MathChallengeFactory(translator=translator, locale="de")
    spec = await factory.create()
    assert " = ?" in spec.prompt
