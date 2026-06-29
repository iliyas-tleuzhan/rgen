"""Symbolic multi-step sequence generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Difficulty, Scene, RobotTask
from rgen.utils import choose_instruction_template, default_robot, generator_metadata, make_object


class MultiStepSequenceGenerator:
    task_type = "multi_step_sequence"

    def generate(self, context: GenerationContext) -> RobotTask:
        drawer = make_object(context.rng, "gray", "drawer", movable=False)
        cube = make_object(context.rng, "red", "cube")
        objects = [drawer, cube]
        if context.difficulty in {Difficulty.medium, Difficulty.hard}:
            objects.append(make_object(context.rng, "blue", "cube", 1))
        constraints = [
            "complete subtasks in order",
            "drawer must be open before placing object inside",
            "drawer must be closed after placement",
            "respect workspace bounds",
        ]
        if context.difficulty == Difficulty.hard:
            constraints.extend(["ignore distractor object", "verify drawer state after each manipulation"])
        plan = [
            "validate_scene",
            "move_to_drawer_handle",
            "open_drawer",
            "move_to_red_cube",
            "grasp_red_cube",
            "place_red_cube_in_drawer",
            "release_red_cube",
            "close_drawer",
            "verify_sequence_complete",
        ]
        return RobotTask(
            id=context.task_id,
            instruction=choose_instruction_template(
                context.rng,
                [
                    "Open the drawer, place the red cube inside it, then close the drawer.",
                    "Complete the ordered sequence: open {drawer}, move {cube} inside, and close {drawer}.",
                    "Move the required cube into the drawer only after opening it, then restore the drawer closed.",
                ],
                drawer=drawer.name,
                cube=cube.name,
            ),
            task_type=self.task_type,
            difficulty=context.difficulty,
            robot=default_robot(),
            scene=Scene(objects=objects, zones=[]),
            objects=objects,
            zones=[],
            constraints=constraints,
            expected_plan=plan,
            safety_checks=["workspace_bounds_check", "gripper_state_check", "ordered_subtask_check"],
            metadata=generator_metadata(
                context.seed,
                ambiguity="explicit" if context.difficulty != Difficulty.hard else "mild_ambiguous",
                resolved_references={"drawer": drawer.name, "payload": cube.name},
                tags=["multi_step", "ordered_subtasks", "symbolic_state"],
            ),
        )
