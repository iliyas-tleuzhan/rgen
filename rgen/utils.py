"""Shared helpers for deterministic generation."""

from __future__ import annotations

import random
from collections.abc import Sequence

from rgen import __version__
from rgen.schemas import Bounds, ObjectSpec, Robot, Workspace, Zone


COLORS = ("red", "blue", "green", "yellow", "purple", "orange")
SHAPES = ("cube", "cylinder", "sphere")


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


def make_bin(rng: random.Random, color: str) -> ObjectSpec:
    return ObjectSpec(
        name=f"{color}_bin",
        type="container",
        color=color,
        position=point_in_workspace(rng),
        size=(0.14, 0.14, 0.1),
        movable=False,
    )


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


def generator_metadata(seed: int | None, *, is_solvable: bool = True, explanation: str | None = None) -> dict[str, object]:
    return {
        "generator_version": __version__,
        "seed": seed,
        "is_solvable": is_solvable,
        "explanation": explanation,
    }

