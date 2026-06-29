from rgen.cli import generate_tasks
from rgen.generators import GENERATORS, GenerationContext
from rgen.schemas import Difficulty
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

