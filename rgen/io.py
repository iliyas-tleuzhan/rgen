"""Dataset read/write helpers."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

import yaml

from rgen.schemas import RobotTask


def write_tasks(tasks: Iterable[RobotTask], path: Path, fmt: str | None = None) -> None:
    task_list = list(tasks)
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = (fmt or path.suffix.removeprefix(".") or "jsonl").lower()
    if fmt == "jsonl":
        with path.open("w", encoding="utf-8") as f:
            for task in task_list:
                f.write(task.model_dump_json() + "\n")
    elif fmt in {"yaml", "yml"}:
        with path.open("w", encoding="utf-8") as f:
            yaml.safe_dump([task.model_dump(mode="json") for task in task_list], f, sort_keys=False)
    elif fmt == "csv":
        with path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "id",
                    "instruction",
                    "task_type",
                    "difficulty",
                    "ambiguity",
                    "is_solvable",
                    "failure_mode",
                    "plan_length",
                ],
            )
            writer.writeheader()
            for task in task_list:
                writer.writerow(
                    {
                        "id": task.id,
                        "instruction": task.instruction,
                        "task_type": task.task_type.value,
                        "difficulty": task.difficulty.value,
                        "ambiguity": task.metadata.ambiguity.value,
                        "is_solvable": task.metadata.is_solvable,
                        "failure_mode": task.metadata.failure_mode,
                        "plan_length": len(task.expected_plan),
                    }
                )
    else:
        raise ValueError(f"Unsupported format: {fmt}")


def read_tasks(path: Path) -> list[RobotTask]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return [RobotTask.model_validate_json(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if suffix in {".yaml", ".yml"}:
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        return [RobotTask.model_validate(item) for item in raw]
    raise ValueError(f"Unsupported input format: {suffix}")
