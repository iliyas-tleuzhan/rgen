"""Markdown dataset report generation."""

from __future__ import annotations

from pathlib import Path

from rgen.io import read_tasks
from rgen.stats import compute_stats
from rgen.validators import validate_dataset


def _table(title: str, rows: list[tuple[str, object]]) -> str:
    lines = [f"### {title}", "", "| Metric | Value |", "| --- | ---: |"]
    lines.extend(f"| {key} | {value} |" for key, value in rows)
    return "\n".join(lines)


def _distribution(title: str, counts: dict[str, int]) -> str:
    rows = sorted(counts.items())
    if not rows:
        rows = [("none", 0)]
    return _table(title, [(name, count) for name, count in rows])


def quality_warnings(errors: list[str]) -> list[str]:
    warnings: list[str] = []
    if errors:
        warnings.append(f"Validation found {len(errors)} issue(s); inspect the validation summary before using this dataset.")
    else:
        warnings.append("No validation errors were found.")
    return warnings


def build_report(path: Path) -> str:
    tasks = read_tasks(path)
    _, errors = validate_dataset(path)
    stats = compute_stats(tasks)
    examples = tasks[:5]
    parts = [
        f"# RGen Dataset Report\n\nDataset path: `{path}`",
        _table(
            "Summary",
            [
                ("Total tasks", stats.total),
                ("Solvable tasks", stats.solvable_count),
                ("Impossible tasks", stats.impossible_count),
                ("Average plan length", f"{stats.average_plan_length:.2f}"),
                ("Average objects", f"{stats.average_objects:.2f}"),
                ("Average constraints", f"{stats.average_constraints:.2f}"),
                ("Average zones", f"{stats.average_zones:.2f}"),
            ],
        ),
        _distribution("Task Type Distribution", dict(stats.task_type_counts)),
        _distribution("Difficulty Distribution", dict(stats.difficulty_counts)),
        _distribution("Ambiguity Distribution", dict(stats.ambiguity_counts)),
        _distribution("Failure Mode Distribution", dict(stats.failure_mode_counts)),
        _distribution("Most Common Constraints", dict(stats.constraint_counts.most_common(10))),
        _distribution("Most Common Safety Checks", dict(stats.safety_check_counts.most_common(10))),
        _table("Validation Summary", [("Errors", len(errors))]),
        "### Dataset Quality Warnings\n\n" + "\n".join(f"- {warning}" for warning in quality_warnings(errors)),
        "### Recommended Use Cases\n\n"
        "- LLM robot planner evaluation\n"
        "- Spatial-reference reasoning benchmarks\n"
        "- Safety-checking and rejection behavior tests\n"
        "- Curriculum generation from easy to hard symbolic tasks",
        "### Example Tasks\n\n"
        + "\n\n".join(
            f"#### {task.id}\n\n"
            f"- Type: `{task.task_type.value}`\n"
            f"- Difficulty: `{task.difficulty.value}`\n"
            f"- Ambiguity: `{task.metadata.ambiguity.value}`\n"
            f"- Instruction: {task.instruction}\n"
            f"- Plan length: {len(task.expected_plan)}"
            for task in examples
        ),
    ]
    if errors:
        parts.append("### Validation Errors\n\n" + "\n".join(f"- {error}" for error in errors[:25]))
    return "\n\n".join(parts) + "\n"


def write_report(path: Path, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(build_report(path), encoding="utf-8")
