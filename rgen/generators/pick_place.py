"""Pick-and-place task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Difficulty, Scene, RobotTask
from rgen.utils import (
    COLORS,
    CONTAINERS,
    SHAPES,
    choose,
    choose_instruction_template,
    default_robot,
    forbidden_zone,
    generator_metadata,
    make_container,
    make_distractor_objects,
    make_object,
)


class PickAndPlaceGenerator:
    task_type = "pick_and_place"

    def generate(self, context: GenerationContext) -> RobotTask:
        color = choose(context.rng, COLORS)
        shape = choose(context.rng, SHAPES)
        item = make_object(context.rng, color, shape)
        target_color = choose(context.rng, tuple(c for c in COLORS if c != color))
        container = make_container(context.rng, target_color, choose(context.rng, CONTAINERS[:3]))
        objects = [item, container]
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
            objects.extend(make_distractor_objects(context.rng, 3))
            constraints.extend(["ignore distractor objects", "keep object upright during transport"])
        ambiguity = "explicit"
        if context.difficulty == Difficulty.hard:
            ambiguity = "mild_ambiguous"
        if context.rng.random() < 0.12:
            ambiguity = "underspecified"
            constraints.append("ask for clarification before execution")
        instruction = choose_instruction_template(
            context.rng,
            [
                "Pick up the {item}, ignore distractors, and place it inside the {container}.",
                "Move the {item} into the {container} without violating safety constraints.",
                "Move the object closest to the {container} into the matching container while avoiding restricted zones.",
            ],
            item=item.name,
            container=container.name,
        )
        if ambiguity == "underspecified":
            instruction = f"Move the {color} object to a container."
        plan = [
            "validate_scene",
            "check_workspace_bounds",
            f"plan_path_to_{item.name}",
            "open_gripper",
            "move_to_pregrasp",
            "move_to_grasp",
            "close_gripper",
            "lift_object",
            f"plan_path_to_{container.name}",
            "place_object",
            "open_gripper",
            "verify_task_success",
        ]
        return RobotTask(
            id=context.task_id,
            instruction=instruction,
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
            metadata=generator_metadata(
                context.seed,
                ambiguity=ambiguity,
                requires_clarification=ambiguity == "underspecified",
                clarification_question=f"Which {color} object should be moved?" if ambiguity == "underspecified" else None,
                resolved_references={"target_object": item.name, "target_container": container.name}
                if ambiguity != "underspecified"
                else {},
                tags=["pick_and_place", "grasping"] + (["forbidden_zone"] if zones else []) + (["ambiguous"] if ambiguity != "explicit" else []),
            ),
        )
