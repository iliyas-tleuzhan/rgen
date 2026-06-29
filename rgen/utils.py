"""Shared helpers for deterministic generation."""

from __future__ import annotations

import math
import random
from collections.abc import Sequence

from rgen import __version__
from rgen.schemas import Bounds, ObjectSpec, Robot, Workspace, Zone


COLORS = ("red", "blue", "green", "yellow", "purple", "orange")
SHAPES = ("cube", "cylinder", "sphere", "block")
CONTAINERS = ("bin", "tray", "basket", "target_area", "shelf")


def default_robot() -> Robot:
    return Robot(
        workspace=Workspace(x=(-0.5, 0.5), y=(-0.5, 0.5), z=(0.0, 0.8)),
        gripper=True,
        max_speed=0.35,
    )


def point_in_workspace(rng: random.Random, z: float = 0.05) -> tuple[float, float, float]:
    return (round(rng.uniform(-0.42, 0.42), 3), round(rng.uniform(-0.42, 0.42), 3), z)


def object_name(color: str, shape: str, index: int | None = None) -> str:
    suffix = "" if index is None else f"_{index}"
    return f"{color}_{shape}{suffix}"


def make_object(
    rng: random.Random,
    color: str,
    shape: str = "cube",
    index: int | None = None,
    movable: bool = True,
) -> ObjectSpec:
    return ObjectSpec(
        name=object_name(color, shape, index),
        type=shape,
        color=color,
        position=point_in_workspace(rng),
        size=(0.04, 0.04, 0.04),
        movable=movable,
    )


def make_container(rng: random.Random, color: str, kind: str = "bin") -> ObjectSpec:
    return ObjectSpec(
        name=f"{color}_{kind}",
        type="container" if kind in {"bin", "tray", "basket"} else kind,
        color=color,
        position=point_in_workspace(rng),
        size=(0.14, 0.14, 0.1),
        movable=False,
    )


def make_bin(rng: random.Random, color: str) -> ObjectSpec:
    return make_container(rng, color, "bin")


def make_tray(rng: random.Random, color: str) -> ObjectSpec:
    return make_container(rng, color, "tray")


def make_target_area(rng: random.Random, color: str = "green") -> ObjectSpec:
    return make_container(rng, color, "target_area")


def make_shelf(rng: random.Random, color: str = "gray") -> ObjectSpec:
    return make_container(rng, color, "shelf")


def make_distractor_objects(rng: random.Random, count: int, start_index: int = 0) -> list[ObjectSpec]:
    return [
        make_object(rng, choose(rng, COLORS), choose(rng, SHAPES), start_index + idx)
        for idx in range(count)
    ]


def forbidden_zone(name: str, rng: random.Random, scale: float = 1.0) -> Zone:
    cx = rng.uniform(-0.2, 0.2)
    cy = rng.uniform(-0.2, 0.2)
    half = 0.08 * scale
    return Zone(
        name=name,
        type="forbidden",
        bounds=Bounds(
            x=(round(cx - half, 3), round(cx + half, 3)),
            y=(round(cy - half, 3), round(cy + half, 3)),
            z=(0.0, round(0.35 * scale, 3)),
        ),
    )


def choose(rng: random.Random, values: Sequence[str]) -> str:
    return values[rng.randrange(len(values))]


def choose_instruction_template(rng: random.Random, templates: Sequence[str], **values: object) -> str:
    return choose(rng, templates).format(**values)


def distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((left - right) ** 2 for left, right in zip(a, b, strict=True)))


def leftmost(objects: Sequence[ObjectSpec]) -> ObjectSpec:
    return min(objects, key=lambda obj: (obj.position[0], obj.name))


def rightmost(objects: Sequence[ObjectSpec]) -> ObjectSpec:
    return max(objects, key=lambda obj: (obj.position[0], obj.name))


def closest_to(objects: Sequence[ObjectSpec], target: ObjectSpec) -> ObjectSpec:
    return min(objects, key=lambda obj: (distance(obj.position, target.position), obj.name))


def farthest_from(objects: Sequence[ObjectSpec], target: ObjectSpec) -> ObjectSpec:
    return max(objects, key=lambda obj: (distance(obj.position, target.position), obj.name))


def generator_metadata(
    seed: int | None,
    *,
    is_solvable: bool = True,
    explanation: str | None = None,
    ambiguity: str = "explicit",
    requires_clarification: bool = False,
    clarification_question: str | None = None,
    failure_mode: str | None = None,
    resolved_references: dict[str, str] | None = None,
    tags: list[str] | None = None,
) -> dict[str, object]:
    return {
        "generator_version": __version__,
        "seed": seed,
        "is_solvable": is_solvable,
        "explanation": explanation,
        "ambiguity": ambiguity,
        "requires_clarification": requires_clarification,
        "clarification_question": clarification_question,
        "failure_mode": failure_mode,
        "resolved_references": resolved_references or {},
        "tags": tags or [],
    }
