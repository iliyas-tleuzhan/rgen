"""Object sorting task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Difficulty, Scene, RobotTask
from rgen.utils import COLORS, default_robot, forbidden_zone, generator_metadata, make_bin, make_object


class SortObjectsGenerator:
    task_type = "sort_objects"

    def generate(self, context: GenerationContext) -> RobotTask:
        colors = list(COLORS[: 2 if context.difficulty == Difficulty.easy else 3])
        repeats = 1 if context.difficulty == Difficulty.easy else 2
        objects = []
        for color in colors:
            objects.append(make_bin(context.rng, color))
            for idx in range(repeats):
                objects.append(make_object(context.rng, color, "cube", idx))
        zones = [forbidden_zone("sorting_no_go_zone", context.rng)] if context.difficulty == Difficulty.hard else []
        constraints = ["match each object color to the same-color bin", "grasp one object at a time", "respect workspace bounds"]
        if zones:
            constraints.append("avoid forbidden zones")
        plan = ["validate_scene", "check_workspace_bounds"]
        for color in colors:
            for idx in range(repeats):
                plan.extend(
                    [
                        f"pick_{color}_cube_{idx}",
                        f"move_to_{color}_bin",
                        f"place_{color}_cube_{idx}",
                    ]
                )
        plan.append("verify_all_objects_sorted")
        return RobotTask(
            id=context.task_id,
            instruction="Sort all colored cubes into their matching colored bins.",
            task_type=self.task_type,
            difficulty=context.difficulty,
            robot=default_robot(),
            scene=Scene(objects=objects, zones=zones),
            objects=objects,
            zones=zones,
            constraints=constraints,
            expected_plan=plan,
            safety_checks=["workspace_bounds_check", "object_attachment_check", "bin_match_check"],
            metadata=generator_metadata(context.seed),
        )

