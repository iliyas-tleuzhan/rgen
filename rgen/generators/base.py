"""Base interfaces for symbolic task generators."""

from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Protocol

from rgen.schemas import Difficulty, RobotTask


@dataclass(frozen=True)
class GenerationContext:
    task_id: str
    seed: int | None
    difficulty: Difficulty
    rng: random.Random


class BaseGenerator(Protocol):
    task_type: str

    def generate(self, context: GenerationContext) -> RobotTask:
        """Generate one task."""


def difficulty_counts(difficulty: Difficulty) -> tuple[int, int]:
    if difficulty == Difficulty.easy:
        return 1, 0
    if difficulty == Difficulty.medium:
        return 2, 1
    return 4, 2

