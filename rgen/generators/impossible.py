"""Intentionally impossible task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Bounds, Difficulty, RobotTask, Scene, Zone
from rgen.utils import default_robot, generator_metadata, make_bin, make_object


class ImpossibleTaskGenerator:
    task_type = "impossible_task"

    def generate(self, context: GenerationContext) -> RobotTask:
        failure_mode = context.rng.choice(
            [
                "unreachable_target",
                "missing_required_object",
                "conflicting_constraints",
                "fully_blocked_workspace",
                "no_matching_container",
                "ambiguous_without_resolution",
            ]
        )
        obj = make_object(context.rng, "red", "cube")
        bin_obj = make_bin(context.rng, "blue")
        zones = []
        objects = [obj, bin_obj]
        instruction = "Move the red cube to an unreachable target."
        explanation = "The target is outside the robot workspace."
        constraints = ["respect workspace bounds", "complete requested manipulation"]
        detect_step = f"detect_{failure_mode}"
        ambiguity = "explicit"
        requires_clarification = False
        clarification_question = None
        if failure_mode == "missing_required_object":
            objects = [bin_obj]
            instruction = "Move the missing red cube into the blue bin."
            explanation = "The required red cube is missing from the scene."
        elif failure_mode == "conflicting_constraints":
            zones = [Zone(name="handoff_zone", type="forbidden", bounds=Bounds(x=(-0.1, 0.1), y=(-0.1, 0.1), z=(0.0, 0.4)))]
            instruction = "Move the red cube through the handoff_zone while avoiding the handoff_zone."
            explanation = "The constraints require entering and avoiding the same zone."
            constraints.extend(["enter handoff_zone", "avoid forbidden zones"])
        elif failure_mode == "fully_blocked_workspace":
            zones = [
                Zone(
                    name="fully_blocked_workspace",
                    type="forbidden",
                    bounds=Bounds(x=(-0.5, 0.5), y=(-0.5, 0.5), z=(0.0, 0.8)),
                )
            ]
            instruction = "Move the red cube while avoiding the fully blocked workspace."
            explanation = "The forbidden zone covers the entire robot workspace."
            constraints.append("avoid forbidden zones")
        elif failure_mode == "no_matching_container":
            objects = [obj, make_bin(context.rng, "green")]
            instruction = "Place the red cube into the matching red container."
            explanation = "No matching red container exists in the scene."
        elif failure_mode == "ambiguous_without_resolution":
            objects = [make_object(context.rng, "red", "cube", 1), make_object(context.rng, "red", "cube", 2)]
            instruction = "Move the red cube into the target container."
            explanation = "Multiple red cubes match the instruction and no resolution rule is provided."
            ambiguity = "underspecified"
            requires_clarification = True
            clarification_question = "Which red cube should be moved?"
        return RobotTask(
            id=context.task_id,
            instruction=instruction,
            task_type=self.task_type,
            difficulty=Difficulty.impossible,
            robot=default_robot(),
            scene=Scene(objects=objects, zones=zones),
            objects=objects,
            zones=zones,
            constraints=constraints,
            expected_plan=["validate_scene", "check_solvability", detect_step, "reject_task_with_explanation"],
            safety_checks=["workspace_bounds_check", "forbidden_zone_check", "solvability_check"],
            metadata=generator_metadata(
                context.seed,
                is_solvable=False,
                explanation=explanation,
                ambiguity=ambiguity,
                requires_clarification=requires_clarification,
                clarification_question=clarification_question,
                failure_mode=failure_mode,
                tags=["impossible_task", failure_mode],
            ),
        )
