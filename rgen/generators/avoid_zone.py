"""Avoid-zone motion task generation."""

from __future__ import annotations

from rgen.generators.base import GenerationContext
from rgen.schemas import Difficulty, Scene, RobotTask
from rgen.utils import choose_instruction_template, default_robot, forbidden_zone, generator_metadata, make_target_area, point_in_workspace


class AvoidZoneGenerator:
    task_type = "avoid_zone"

    def generate(self, context: GenerationContext) -> RobotTask:
        zone_count = 1 if context.difficulty in {Difficulty.easy, Difficulty.medium} else 3
        zones = [forbidden_zone(f"restricted_zone_{i + 1}", context.rng, scale=1.0 + i * 0.15) for i in range(zone_count)]
        safe_zone = make_target_area(context.rng, "green")
        start = point_in_workspace(context.rng, z=0.2)
        goal = point_in_workspace(context.rng, z=0.2)
        constraints = ["avoid forbidden zones", "respect workspace bounds", "maintain clearance from restricted zone boundaries"]
        if context.difficulty == Difficulty.hard:
            constraints.extend(["prefer shortest safe path", "pause before entering narrow passage"])
        return RobotTask(
            id=context.task_id,
            instruction=choose_instruction_template(
                context.rng,
                [
                    "Move from symbolic waypoint {start} to waypoint {goal} without entering any restricted zone.",
                    "Move the end effector to the {safe_zone} while avoiding the blocked corridor.",
                    "Reach the safe zone without passing through any no-go zone.",
                ],
                start=start,
                goal=goal,
                safe_zone=safe_zone.name,
            ),
            task_type=self.task_type,
            difficulty=context.difficulty,
            robot=default_robot(),
            scene=Scene(objects=[safe_zone], zones=zones),
            objects=[safe_zone],
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
            metadata=generator_metadata(
                context.seed,
                ambiguity="mild_ambiguous" if context.difficulty == Difficulty.hard else "explicit",
                resolved_references={"safe_zone": safe_zone.name},
                tags=["avoid_zone", "forbidden_zone", "path_planning"],
            ),
        )
