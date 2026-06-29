"""Reach-target task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Scene, RobotTask
from rgen.utils import choose_instruction_template, default_robot, forbidden_zone, generator_metadata, make_target_area, point_in_workspace


class ReachTargetGenerator:
    task_type = "reach_target"

    def generate(self, context: GenerationContext) -> RobotTask:
        zones = []
        if context.difficulty.value in {"medium", "hard"}:
            zones.append(forbidden_zone("restricted_zone", context.rng))
        target_area = make_target_area(context.rng, "green")
        target = point_in_workspace(context.rng, z=0.25)
        constraints = ["respect workspace bounds", "maintain controlled speed"]
        if zones:
            constraints.append("avoid forbidden zones")
        if context.difficulty.value == "hard":
            constraints.extend(["minimize path length", "keep end effector above table except at target"])
        ambiguity = "mild_ambiguous" if context.difficulty.value == "hard" else "explicit"
        instruction = choose_instruction_template(
            context.rng,
            [
                "Reach the target above the table while keeping the end effector outside the no-go zone.",
                "Move the robot end effector to {target} and finish inside the {target_area}.",
                "Navigate to the {target_area} target without violating workspace limits.",
            ],
            target=target,
            target_area=target_area.name,
        )
        plan = ["validate_scene", "check_workspace_bounds", "plan_path_to_target"]
        if zones:
            plan.append("verify_path_avoids_restricted_zone")
        plan.extend(["move_to_target", "verify_target_reached"])
        return RobotTask(
            id=context.task_id,
            instruction=instruction,
            task_type=self.task_type,
            difficulty=context.difficulty,
            robot=default_robot(),
            scene=Scene(objects=[target_area], zones=zones),
            objects=[target_area],
            zones=zones,
            constraints=constraints,
            expected_plan=plan,
            safety_checks=["workspace_bounds_check", "speed_limit_check"] + (["forbidden_zone_check"] if zones else []),
            metadata=generator_metadata(
                context.seed,
                ambiguity=ambiguity,
                resolved_references={"target_area": target_area.name},
                tags=["reach_target", "workspace"] + (["forbidden_zone"] if zones else []),
            ),
        )
