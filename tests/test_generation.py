from rgen.cli import generate_tasks
from rgen.generators import GENERATORS, GenerationContext
from rgen.schemas import Difficulty, TaskType
import random


def test_generation_produces_requested_number_of_tasks():
    tasks = generate_tasks(n=12, difficulty="mixed", seed=42)
    assert len(tasks) == 12
    assert tasks[0].id == "rgen_000001"


def test_seed_determinism_works():
    first = [task.model_dump(mode="json") for task in generate_tasks(n=10, difficulty="mixed", seed=42)]
    second = [task.model_dump(mode="json") for task in generate_tasks(n=10, difficulty="mixed", seed=42)]
    assert first == second


def test_all_task_types_can_generate_valid_tasks():
    for idx, (task_type, generator_cls) in enumerate(GENERATORS.items(), start=1):
        difficulty = Difficulty.impossible if task_type == "impossible_task" else Difficulty.medium
        context = GenerationContext(
            task_id=f"rgen_{idx:06d}",
            seed=123,
            difficulty=difficulty,
            rng=random.Random(123 + idx),
        )
        task = generator_cls().generate(context)
        assert task.task_type.value == task_type
        assert task.id == f"rgen_{idx:06d}"


def test_spatial_relation_tasks_generate_resolved_references():
    tasks = [task for task in generate_tasks(n=30, difficulty="mixed", seed=7) if task.task_type == TaskType.spatial_relation]
    assert tasks
    assert all(task.metadata.resolved_references for task in tasks)
    assert all(task.metadata.ambiguity.value == "mild_ambiguous" for task in tasks)


def test_ambiguity_metadata_exists():
    tasks = generate_tasks(n=8, difficulty="mixed", seed=42)
    assert all(task.metadata.ambiguity for task in tasks)
    assert all(task.metadata.tags for task in tasks)


def test_impossible_tasks_include_failure_mode_and_rejection_plan():
    tasks = generate_tasks(n=10, difficulty="impossible", seed=42)
    assert all(not task.metadata.is_solvable for task in tasks)
    assert all(task.metadata.failure_mode for task in tasks)
    assert all(task.expected_plan[-1] == "reject_task_with_explanation" for task in tasks)


def test_underspecified_tasks_require_clarification():
    tasks = generate_tasks(n=200, difficulty="mixed", seed=3)
    underspecified = [task for task in tasks if task.metadata.ambiguity.value == "underspecified"]
    assert underspecified
    assert all(task.metadata.requires_clarification for task in underspecified)
    assert all(task.metadata.clarification_question for task in underspecified)
