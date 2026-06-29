"""Pick-and-place task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Difficulty, Scene, RobotTask
from rgen.utils import COLORS, SHAPES, choose, default_robot, forbidden_zone, generator_metadata, make_bin, make_object


class PickAndPlaceGenerator:
    task_type = "pick_and_place"

    def generate(self, context: GenerationContext) -> RobotTask:
        color = choose(context.rng, COLORS)
        shape = choose(context.rng, SHAPES)
        item = make_object(context.rng, color, shape)
        target_color = choose(context.rng, tuple(c for c in COLORS if c != color))
        bin_obj = make_bin(context.rng, target_color)
        objects = [item, bin_obj]
        zones = []
        constraints = [
            "respect workspace bounds",
            "object must be grasped before transport",
            "release object only above target container",
        ]
        if context.difficulty in {Difficulty.medium, Difficulty.hard}:
            zones.append(forbidden_zone("restricted_zone", context.rng))
            constraints.append("avoid forbidden zones")
        if context.difficulty == Difficulty.hard:
            objects.extend(make_object(context.rng, choose(context.rng, COLORS), "cube", i) for i in range(2))
            constraints.extend(["ignore distractor objects", "keep object upright during transport"])
        plan = [
            "validate_scene",
            "check_workspace_bounds",
            f"plan_path_to_{item.name}",
            "open_gripper",
            "move_to_pregrasp",
            "move_to_grasp",
            "close_gripper",
            "lift_object",
            f"plan_path_to_{bin_obj.name}",
            "place_object",
            "open_gripper",
            "verify_task_success",
        ]
        return RobotTask(
            id=context.task_id,
            instruction=f"Move the {item.name} into the {bin_obj.name} without violating safety constraints.",
            task_type=self.task_type,
            difficulty=context.difficulty,
            robot=default_robot(),
            scene=Scene(objects=objects, zones=zones),
            objects=objects,
            zones=zones,
            constraints=constraints,
            expected_plan=plan,
            safety_checks=["workspace_bounds_check", "gripper_state_check", "object_attachment_check"]
            + (["forbidden_zone_check"] if zones else []),
            metadata=generator_metadata(context.seed),
        )

