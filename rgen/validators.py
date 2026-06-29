"""Dataset validation utilities."""

from __future__ import annotations

from pathlib import Path

from pydantic import ValidationError

from rgen.io import read_tasks
from rgen.schemas import AmbiguityLevel, Difficulty, RobotTask, TaskType


SYMBOLIC_REFERENCE_WORDS = {
    "target",
    "object",
    "cube",
    "cylinder",
    "sphere",
    "block",
    "bin",
    "tray",
    "basket",
    "drawer",
    "shelf",
    "zone",
    "leftmost",
    "rightmost",
    "closest",
    "farthest",
    "matching",
    "workspace",
}


def validate_task(task: RobotTask) -> list[str]:
    errors: list[str] = []
    workspace = task.robot.workspace
    object_names = [obj.name for obj in task.objects]
    duplicate_object_names = sorted({name for name in object_names if object_names.count(name) > 1})
    for name in duplicate_object_names:
        errors.append(f"{task.id}: duplicate object name '{name}'")
    for obj in task.objects:
        x, y, z = obj.position
        if not (workspace.x[0] <= x <= workspace.x[1] and workspace.y[0] <= y <= workspace.y[1] and workspace.z[0] <= z <= workspace.z[1]):
            errors.append(f"{task.id}: object {obj.name} position is outside workspace")
    for zone in task.zones:
        for axis in ("x", "y", "z"):
            lo, hi = getattr(zone.bounds, axis)
            if lo >= hi:
                errors.append(f"{task.id}: zone {zone.name} has invalid {axis} bounds")
        if (
            zone.type == "forbidden"
            and zone.bounds.x[0] <= workspace.x[0]
            and zone.bounds.x[1] >= workspace.x[1]
            and zone.bounds.y[0] <= workspace.y[0]
            and zone.bounds.y[1] >= workspace.y[1]
            and zone.bounds.z[0] <= workspace.z[0]
            and zone.bounds.z[1] >= workspace.z[1]
            and task.metadata.is_solvable
        ):
            errors.append(f"{task.id}: forbidden zone '{zone.name}' covers the entire workspace for a solvable task")
    if task.metadata.is_solvable and not task.expected_plan:
        errors.append(f"{task.id}: solvable task has empty expected_plan")
    if not task.metadata.is_solvable:
        if not task.metadata.explanation:
            errors.append(f"{task.id}: impossible task is missing explanation")
        if not task.metadata.failure_mode:
            errors.append(f"{task.id}: impossible task is missing failure_mode")
    if task.metadata.ambiguity == AmbiguityLevel.underspecified and not task.metadata.requires_clarification:
        errors.append(f"{task.id}: underspecified task missing requires_clarification=true")
    if task.metadata.requires_clarification and not task.metadata.clarification_question:
        errors.append(f"{task.id}: task requiring clarification is missing clarification_question")
    if task.task_type == TaskType.spatial_relation and not task.metadata.resolved_references:
        errors.append(f"{task.id}: spatial_relation task missing resolved_references metadata")
    known_names = set(object_names) | {zone.name for zone in task.zones}
    for step in task.expected_plan:
        if step.startswith(("move_to_", "plan_path_to_", "pick_", "place_")):
            if not any(name in step for name in known_names) and not any(
                token in step
                for token in (
                    "target",
                    "selected_object",
                    "selected_cube",
                    "object",
                    "pregrasp",
                    "grasp",
                    "safe_zone",
                    "drawer_handle",
                )
            ):
                errors.append(f"{task.id}: plan step '{step}' does not reference a known object, zone, or symbolic target")
    instruction = task.instruction.lower()
    if not any(name.lower() in instruction for name in known_names) and not any(word in instruction for word in SYMBOLIC_REFERENCE_WORDS):
        errors.append(f"{task.id}: instruction does not mention an object, target, zone, or symbolic reference")
    if task.difficulty == Difficulty.hard and task.metadata.is_solvable:
        if len(task.objects) < 2 and len(task.zones) < 1 and len(task.constraints) < 4 and len(task.expected_plan) < 7:
            errors.append(f"{task.id}: hard task is not meaningfully more complex than an easy task")
    return errors


def validate_dataset(path: Path) -> tuple[list[RobotTask], list[str]]:
    errors: list[str] = []
    try:
        tasks = read_tasks(path)
    except (ValidationError, ValueError, OSError) as exc:
        return [], [str(exc)]
    seen: set[str] = set()
    for task in tasks:
        if task.difficulty.value not in {item.value for item in Difficulty}:
            errors.append(f"{task.id}: invalid difficulty '{task.difficulty}'")
        if task.task_type.value not in {item.value for item in TaskType}:
            errors.append(f"{task.id}: invalid task type '{task.task_type}'")
        if task.id in seen:
            errors.append(f"{task.id}: duplicate task id")
        seen.add(task.id)
        errors.extend(validate_task(task))
    return tasks, errors
