"""Dataset statistics."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from rgen.schemas import RobotTask


@dataclass(frozen=True)
class DatasetStats:
    total: int
    task_type_counts: Counter[str]
    difficulty_counts: Counter[str]
    ambiguity_counts: Counter[str]
    failure_mode_counts: Counter[str]
    constraint_counts: Counter[str]
    safety_check_counts: Counter[str]
    solvable_count: int
    impossible_count: int
    average_plan_length: float
    average_objects: float
    average_constraints: float
    average_zones: float


def compute_stats(tasks: list[RobotTask]) -> DatasetStats:
    total = len(tasks)
    if total == 0:
        return DatasetStats(0, Counter(), Counter(), Counter(), Counter(), Counter(), Counter(), 0, 0, 0.0, 0.0, 0.0, 0.0)
    solvable = sum(1 for task in tasks if task.metadata.is_solvable)
    return DatasetStats(
        total=total,
        task_type_counts=Counter(task.task_type.value for task in tasks),
        difficulty_counts=Counter(task.difficulty.value for task in tasks),
        ambiguity_counts=Counter(task.metadata.ambiguity.value for task in tasks),
        failure_mode_counts=Counter(task.metadata.failure_mode for task in tasks if task.metadata.failure_mode),
        constraint_counts=Counter(constraint for task in tasks for constraint in task.constraints),
        safety_check_counts=Counter(check for task in tasks for check in task.safety_checks),
        solvable_count=solvable,
        impossible_count=total - solvable,
        average_plan_length=sum(len(task.expected_plan) for task in tasks) / total,
        average_objects=sum(len(task.objects) for task in tasks) / total,
        average_constraints=sum(len(task.constraints) for task in tasks) / total,
        average_zones=sum(len(task.zones) for task in tasks) / total,
    )
