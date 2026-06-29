"""Avoid-zone motion task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Difficulty, Scene, RobotTask
from rgen.utils import default_robot, forbidden_zone, generator_metadata, point_in_workspace


class AvoidZoneGenerator:
    task_type = "avoid_zone"

    def generate(self, context: GenerationContext) -> RobotTask:
        zone_count = 1 if context.difficulty in {Difficulty.easy, Difficulty.medium} else 3
        zones = [forbidden_zone(f"restricted_zone_{i + 1}", context.rng, scale=1.0 + i * 0.15) for i in range(zone_count)]
        start = point_in_workspace(context.rng, z=0.2)
        goal = point_in_workspace(context.rng, z=0.2)
        constraints = ["avoid forbidden zones", "respect workspace bounds", "maintain clearance from restricted zone boundaries"]
        if context.difficulty == Difficulty.hard:
            constraints.extend(["prefer shortest safe path", "pause before entering narrow passage"])
        return RobotTask(
            id=context.task_id,
            instruction=f"Move from symbolic waypoint {start} to waypoint {goal} without entering any restricted zone.",
            task_type=self.task_type,
            difficulty=context.difficulty,
            robot=default_robot(),
            scene=Scene(objects=[], zones=zones),
            objects=[],
            zones=zones,
            constraints=constraints,
            expected_plan=[
                "validate_scene",
                "check_workspace_bounds",
                "inflate_forbidden_zones",
                "plan_collision_free_path",
                "execute_path",
                "verify_no_zone_entry",
            ],
            safety_checks=["workspace_bounds_check", "forbidden_zone_check", "clearance_check"],
            metadata=generator_metadata(context.seed),
        )

