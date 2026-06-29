"""Generate a small deterministic dataset."""

from pathlib import Path

from rgen.cli import generate_tasks
from rgen.io import write_tasks


if __name__ == "__main__":
    output = Path("data/small.jsonl")
    tasks = generate_tasks(n=10, difficulty="medium", seed=7)
    write_tasks(tasks, output)
    print(f"Generated {len(tasks)} tasks at {output}")

