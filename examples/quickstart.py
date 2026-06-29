"""Quickstart example for generating a small RGen dataset."""

from pathlib import Path

from rgen.cli import generate_tasks
from rgen.io import write_tasks


tasks = generate_tasks(n=5, difficulty="mixed", seed=42)
write_tasks(tasks, Path("data/example_quickstart.jsonl"))
print(f"Wrote {len(tasks)} tasks to data/example_quickstart.jsonl")

