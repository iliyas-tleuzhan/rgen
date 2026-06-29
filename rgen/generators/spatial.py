"""Spatial-relation task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Difficulty, Scene, RobotTask
from rgen.utils import (
    COLORS,
    closest_to,
    default_robot,
    farthest_from,
    forbidden_zone,
    generator_metadata,
    leftmost,
    make_bin,
    make_object,
    make_tray,
    rightmost,
)


class SpatialRelationGenerator:
    task_type = "spatial_relation"

    def generate(self, context: GenerationContext) -> RobotTask:
        colors = list(COLORS[:4])
        movable = [make_object(context.rng, colors[idx], "cube", idx + 1) for idx in range(4)]
        blue_bin = make_bin(context.rng, "blue")
        green_tray = make_tray(context.rng, "green")
        zones = [forbidden_zone("restricted_zone", context.rng)] if context.difficulty != Difficulty.easy else []
        relation = context.rng.choice(["closest", "leftmost", "rightmost", "farthest"])
        if relation == "closest":
            selected = closest_to(movable, blue_bin)
            reference_key = "closest_object_to_blue_bin"
            instruction = f"Move the cube closest to the {blue_bin.name} into the {green_tray.name}"
            resolve_step = "resolve_spatial_reference_closest_to_blue_bin"
            tag = "closest_object"
        elif relation == "leftmost":
            selected = leftmost(movable)
            reference_key = "leftmost_cube"
            instruction = f"Move the leftmost movable cube into the {green_tray.name}"
            resolve_step = "resolve_spatial_reference_leftmost_cube"
            tag = "leftmost_object"
        elif relation == "rightmost":
            selected = rightmost(movable)
            reference_key = "rightmost_cube"
            instruction = f"Move the rightmost movable cube into the {green_tray.name}"
            resolve_step = "resolve_spatial_reference_rightmost_cube"
            tag = "rightmost_object"
        else:
            selected = farthest_from(movable, green_tray)
            reference_key = "farthest_object_from_green_tray"
            instruction = f"Move the cube farthest from the {green_tray.name} into that tray"
            resolve_step = "resolve_spatial_reference_farthest_from_green_tray"
            tag = "farthest_object"
        if zones:
            instruction += " without entering the restricted zone"
        instruction += "."
        constraints = ["resolve spatial reference before motion", "respect workspace bounds", "grasp selected object before transport"]
        if zones:
            constraints.append("avoid forbidden zones")
        if context.difficulty == Difficulty.hard:
            constraints.extend(["ignore non-selected cubes", "verify selected object identity before grasp"])
        return RobotTask(
            id=context.task_id,
            instruction=instruction,
            task_type=self.task_type,
            difficulty=context.difficulty,
            robot=default_robot(),
            scene=Scene(objects=[*movable, blue_bin, green_tray], zones=zones),
            objects=[*movable, blue_bin, green_tray],
            zones=zones,
            constraints=constraints,
            expected_plan=[
                "validate_scene",
                resolve_step,
                "check_workspace_bounds",
                "check_forbidden_zones",
                f"move_to_{selected.name}",
                "grasp_selected_object",
                f"move_to_{green_tray.name}",
                "release_object",
                "verify_task_success",
            ],
            safety_checks=["workspace_bounds_check", "forbidden_zone_check", "resolved_reference_check", "gripper_state_check"],
            metadata=generator_metadata(
                context.seed,
                ambiguity="mild_ambiguous",
                resolved_references={reference_key: selected.name, "target_container": green_tray.name},
                tags=["spatial_reference", tag] + (["forbidden_zone"] if zones else []),
            ),
        )
