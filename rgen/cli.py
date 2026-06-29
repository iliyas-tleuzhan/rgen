"""Command line interface for RGen."""

from __future__ import annotations

import random
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from rgen.generators import GENERATORS, GenerationContext
from rgen.io import read_tasks, write_tasks
from rgen.report import write_report
from rgen.schemas import Difficulty
from rgen.stats import compute_stats
from rgen.validators import validate_dataset

app = typer.Typer(help="Synthetic Robot Dataset Generator")
console = Console()


def _difficulty(value: str, rng: random.Random) -> Difficulty:
    if value == "mixed":
        return rng.choice([Difficulty.easy, Difficulty.medium, Difficulty.hard, Difficulty.impossible])
    return Difficulty(value)


def generate_tasks(n: int, difficulty: str = "mixed", seed: int | None = None) -> list:
    rng = random.Random(seed)
    task_types = list(GENERATORS)
    tasks = []
    for idx in range(1, n + 1):
        diff = _difficulty(difficulty, rng)
        task_type = "impossible_task" if diff == Difficulty.impossible else rng.choice([t for t in task_types if t != "impossible_task"])
        generator = GENERATORS[task_type]()
        context = GenerationContext(task_id=f"rgen_{idx:06d}", seed=seed, difficulty=diff, rng=rng)
        tasks.append(generator.generate(context))
    return tasks


@app.command()
def generate(
    n: Annotated[int, typer.Option("--n", min=1)] = 100,
    out: Annotated[Path, typer.Option("--out")] = Path("data/tasks.jsonl"),
    difficulty: Annotated[str, typer.Option("--difficulty")] = "mixed",
    format: Annotated[str | None, typer.Option("--format")] = None,
    seed: Annotated[int | None, typer.Option("--seed")] = None,
) -> None:
    """Generate a synthetic robotics dataset."""
    tasks = generate_tasks(n=n, difficulty=difficulty, seed=seed)
    write_tasks(tasks, out, format)
    table = Table(title="Generated Dataset")
    table.add_column("Output")
    table.add_column("Tasks", justify="right")
    table.add_column("Difficulty")
    table.add_row(str(out), str(len(tasks)), difficulty)
    console.print(table)


@app.command()
def validate(path: Path) -> None:
    """Validate a JSONL/YAML dataset."""
    tasks, errors = validate_dataset(path)
    table = Table(title="Validation Report")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    table.add_row("Tasks", str(len(tasks)))
    table.add_row("Errors", str(len(errors)))
    console.print(table)
    if errors:
        for error in errors:
            console.print(f"[red]- {error}[/red]")
        raise typer.Exit(1)
    console.print("[green]Dataset is valid.[/green]")


@app.command()
def stats(path: Path) -> None:
    """Print dataset statistics."""
    tasks = read_tasks(path)
    summary = compute_stats(tasks)
    table = Table(title="Dataset Statistics")
    table.add_column("Metric")
    table.add_column("Value", justify="right")
    rows = [
        ("Total tasks", summary.total),
        ("Solvable tasks", summary.solvable_count),
        ("Impossible tasks", summary.impossible_count),
        ("Average plan length", f"{summary.average_plan_length:.2f}"),
        ("Average objects", f"{summary.average_objects:.2f}"),
        ("Average constraints", f"{summary.average_constraints:.2f}"),
        ("Average zones", f"{summary.average_zones:.2f}"),
    ]
    for key, value in rows:
        table.add_row(key, str(value))
    console.print(table)
    for title, counts in (
        ("Task Types", summary.task_type_counts),
        ("Difficulty", summary.difficulty_counts),
        ("Ambiguity", summary.ambiguity_counts),
        ("Failure Modes", summary.failure_mode_counts),
    ):
        count_table = Table(title=title)
        count_table.add_column("Name")
        count_table.add_column("Count", justify="right")
        for name, count in counts.items():
            count_table.add_row(name, str(count))
        console.print(count_table)


@app.command()
def report(path: Path, out: Annotated[Path, typer.Option("--out")] = Path("data/report.md")) -> None:
    """Generate a Markdown dataset quality report."""
    write_report(path, out)
    table = Table(title="Report Generated")
    table.add_column("Dataset")
    table.add_column("Report")
    table.add_row(str(path), str(out))
    console.print(table)


@app.command()
def sample(path: Path, n: Annotated[int, typer.Option("--n", min=1)] = 5) -> None:
    """Print sample task records."""
    tasks = read_tasks(path)
    table = Table(title=f"Sample: {path}")
    table.add_column("ID")
    table.add_column("Type")
    table.add_column("Difficulty")
    table.add_column("Instruction")
    for task in tasks[:n]:
        table.add_row(task.id, task.task_type.value, task.difficulty.value, task.instruction)
    console.print(table)


@app.command()
def split(
    path: Path,
    train: Annotated[float, typer.Option("--train")] = 0.8,
    val: Annotated[float, typer.Option("--val")] = 0.1,
    test: Annotated[float, typer.Option("--test")] = 0.1,
    out_dir: Annotated[Path, typer.Option("--out-dir")] = Path("data/splits"),
    seed: Annotated[int, typer.Option("--seed")] = 42,
) -> None:
    """Split a dataset into train/validation/test JSONL files."""
    if round(train + val + test, 6) != 1.0:
        raise typer.BadParameter("train + val + test must equal 1.0")
    tasks = read_tasks(path)
    rng = random.Random(seed)
    rng.shuffle(tasks)
    train_end = int(len(tasks) * train)
    val_end = train_end + int(len(tasks) * val)
    splits = {
        "train": tasks[:train_end],
        "val": tasks[train_end:val_end],
        "test": tasks[val_end:],
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, split_tasks in splits.items():
        write_tasks(split_tasks, out_dir / f"{name}.jsonl", "jsonl")
    table = Table(title="Dataset Split")
    table.add_column("Split")
    table.add_column("Tasks", justify="right")
    for name, split_tasks in splits.items():
        table.add_row(name, str(len(split_tasks)))
    console.print(table)


if __name__ == "__main__":
    app()
