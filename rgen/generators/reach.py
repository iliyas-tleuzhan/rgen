"""Reach-target task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Scene, RobotTask
from rgen.utils import default_robot, forbidden_zone, generator_metadata, point_in_workspace


class ReachTargetGenerator:
    task_type = "reach_target"

    def generate(self, context: GenerationContext) -> RobotTask:
        zones = []
        if context.difficulty.value in {"medium", "hard"}:
            zones.append(forbidden_zone("restricted_zone", context.rng))
        target = point_in_workspace(context.rng, z=0.25)
        constraints = ["respect workspace bounds", "maintain controlled speed"]
        if zones:
            constraints.append("avoid forbidden zones")
        if context.difficulty.value == "hard":
            constraints.extend(["minimize path length", "keep end effector above table except at target"])
        plan = ["validate_scene", "check_workspace_bounds", "plan_path_to_target"]
        if zones:
            plan.append("verify_path_avoids_restricted_zone")
        plan.extend(["move_to_target", "verify_target_reached"])
        return RobotTask(
            id=context.task_id,
            instruction=f"Move the robot end effector to target position {target} while respecting all constraints.",
            task_type=self.task_type,
            difficulty=context.difficulty,
            robot=default_robot(),
            scene=Scene(objects=[], zones=zones),
            objects=[],
            zones=zones,
            constraints=constraints,
            expected_plan=plan,
            safety_checks=["workspace_bounds_check", "speed_limit_check"] + (["forbidden_zone_check"] if zones else []),
            metadata=generator_metadata(context.seed),
        )

