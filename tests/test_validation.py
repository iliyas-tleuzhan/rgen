from pathlib import Path

from rgen.cli import generate_tasks
from rgen.io import write_tasks
from rgen.schemas import ObjectSpec
from rgen.validators import validate_dataset


def test_validation_accepts_generated_dataset(tmp_path: Path):
    path = tmp_path / "tasks.jsonl"
    write_tasks(generate_tasks(n=5, difficulty="mixed", seed=42), path)
    tasks, errors = validate_dataset(path)
    assert len(tasks) == 5
    assert errors == []


def test_validation_catches_invalid_object_position(tmp_path: Path):
    path = tmp_path / "bad.jsonl"
    task = generate_tasks(n=1, difficulty="easy", seed=1)[0]
    bad_object = ObjectSpec(
        name="bad_cube",
        type="cube",
        position=(99.0, 99.0, 99.0),
        size=(0.04, 0.04, 0.04),
    )
    task.objects.append(bad_object)
    task.scene.objects.append(bad_object)
    write_tasks([task], path)
    _, errors = validate_dataset(path)
    assert any("outside workspace" in error for error in errors)

