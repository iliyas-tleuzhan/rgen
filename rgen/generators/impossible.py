"""Intentionally impossible task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Bounds, Difficulty, RobotTask, Scene, Zone
from rgen.utils import default_robot, generator_metadata, make_object


class ImpossibleTaskGenerator:
    task_type = "impossible_task"

    def generate(self, context: GenerationContext) -> RobotTask:
        reason = context.rng.choice(
            [
                "target is outside the robot workspace",
                "required object is missing from the scene",
                "constraints require entering and avoiding the same zone",
            ]
        )
        obj = make_object(context.rng, "red", "cube")
        zones = [
            Zone(
                name="fully_blocked_workspace",
                type="forbidden",
                bounds=Bounds(x=(-0.5, 0.5), y=(-0.5, 0.5), z=(0.0, 0.8)),
            )
        ]
        constraints = ["respect workspace bounds", "avoid forbidden zones", "complete requested manipulation"]
        return RobotTask(
            id=context.task_id,
            instruction="Move the red cube to an unreachable target while avoiding the fully blocked workspace.",
            task_type=self.task_type,
            difficulty=Difficulty.impossible,
            robot=default_robot(),
            scene=Scene(objects=[obj], zones=zones),
            objects=[obj],
            zones=zones,
            constraints=constraints,
            expected_plan=[],
            safety_checks=["workspace_bounds_check", "forbidden_zone_check", "solvability_check"],
            metadata=generator_metadata(context.seed, is_solvable=False, explanation=reason),
        )

