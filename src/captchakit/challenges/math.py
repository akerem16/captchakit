"""Simple arithmetic challenges."""

from __future__ import annotations

import secrets
from dataclasses import dataclass, field
from typing import Literal

from captchakit.challenges.base import ChallengeSpec
from captchakit.i18n import PromptTranslator

Operator = Literal["+", "-", "*"]


@dataclass(slots=True)
class MathChallengeFactory:
    """Produces easy arithmetic puzzles such as ``"7 + 3 = ?"``.

    Results of subtractions are always non-negative: operands are swapped when
    needed so the user never has to deal with negative numbers.
    """

    min_operand: int = 1
    max_operand: int = 9
    operators: tuple[Operator, ...] = field(default_factory=lambda: ("+", "-"))
    translator: PromptTranslator | None = None
    locale: str = "en"

    def __post_init__(self) -> None:
        if self.min_operand < 0:
            raise ValueError("min_operand must be >= 0")
        if self.max_operand < self.min_operand:
            raise ValueError("max_operand must be >= min_operand")
        if not self.operators:
            raise ValueError("operators must be non-empty")

    def _rand(self) -> int:
        return secrets.randbelow(self.max_operand - self.min_operand + 1) + self.min_operand

    async def create(self) -> ChallengeSpec:
        a = self._rand()
        b = self._rand()
        op: Operator = secrets.choice(self.operators)
        if op == "-" and b > a:
            a, b = b, a
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        else:
            result = a * b
        if self.translator is not None:
            prompt = self.translator.translate("math.ask", self.locale, a=a, op=op, b=b)
        else:
            prompt = f"{a} {op} {b} = ?"
        return ChallengeSpec(prompt=prompt, solution=str(result), case_sensitive=False)
