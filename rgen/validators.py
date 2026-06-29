"""Dataset validation utilities."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from rgen.io import read_tasks
from rgen.schemas import RobotTask


def validate_task(task: RobotTask) -> list[str]:
    errors: list[str] = []
    workspace = task.robot.workspace
    for obj in task.objects:
        x, y, z = obj.position
        if not (workspace.x[0] <= x <= workspace.x[1] and workspace.y[0] <= y <= workspace.y[1] and workspace.z[0] <= z <= workspace.z[1]):
            errors.append(f"{task.id}: object {obj.name} position is outside workspace")
    if task.metadata.is_solvable and not task.expected_plan:
        errors.append(f"{task.id}: solvable task has empty expected_plan")
    if not task.metadata.is_solvable and not task.metadata.explanation:
        errors.append(f"{task.id}: impossible task is missing explanation")
    return errors


def validate_dataset(path: Path) -> tuple[list[RobotTask], list[str]]:
    errors: list[str] = []
    try:
        tasks = read_tasks(path)
    except (ValidationError, ValueError, OSError) as exc:
        return [], [str(exc)]
    seen: set[str] = set()
    for task in tasks:
        if task.id in seen:
            errors.append(f"{task.id}: duplicate task id")
        seen.add(task.id)
        errors.extend(validate_task(task))
    return tasks, errors

