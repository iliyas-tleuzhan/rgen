from pathlib import Path

from rgen.cli import generate_tasks
from rgen.io import read_tasks, write_tasks
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


def test_validation_catches_duplicate_task_ids(tmp_path: Path):
    path = tmp_path / "dupes.jsonl"
    task = generate_tasks(n=1, difficulty="easy", seed=1)[0]
    write_tasks([task, task], path)
    _, errors = validate_dataset(path)
    assert any("duplicate task id" in error for error in errors)


def test_validation_catches_duplicate_object_names(tmp_path: Path):
    path = tmp_path / "bad_names.jsonl"
    task = generate_tasks(n=1, difficulty="easy", seed=1)[0]
    duplicate = task.objects[0].model_copy()
    task.objects.append(duplicate)
    task.scene.objects.append(duplicate)
    write_tasks([task], path)
    _, errors = validate_dataset(path)
    assert any("duplicate object name" in error for error in errors)


def test_invalid_spatial_relation_metadata_is_caught(tmp_path: Path):
    path = tmp_path / "bad_spatial.jsonl"
    task = next(task for task in generate_tasks(n=50, difficulty="mixed", seed=7) if task.task_type.value == "spatial_relation")
    task.metadata.resolved_references = {}
    write_tasks([task], path)
    _, errors = validate_dataset(path)
    assert any("spatial_relation task missing resolved_references" in error for error in errors)


def test_yaml_write_read_works(tmp_path: Path):
    path = tmp_path / "tasks.yaml"
    tasks = generate_tasks(n=4, difficulty="mixed", seed=42)
    write_tasks(tasks, path, "yaml")
    loaded = read_tasks(path)
    assert [task.id for task in loaded] == [task.id for task in tasks]


def test_csv_write_works(tmp_path: Path):
    path = tmp_path / "tasks.csv"
    write_tasks(generate_tasks(n=3, difficulty="easy", seed=42), path, "csv")
    assert "task_type" in path.read_text(encoding="utf-8")


def test_committed_sample_dataset_is_valid():
    path = Path("examples/datasets/sample_tasks.jsonl")
    if path.exists():
        tasks, errors = validate_dataset(path)
        assert tasks
        assert errors == []
