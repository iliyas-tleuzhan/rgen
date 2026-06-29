"""Pydantic schemas for symbolic robot planning tasks."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, model_validator


class Difficulty(str, Enum):
    easy = "easy"
    medium = "medium"
    hard = "hard"
    impossible = "impossible"


class TaskType(str, Enum):
    reach_target = "reach_target"
    pick_and_place = "pick_and_place"
    sort_objects = "sort_objects"
    avoid_zone = "avoid_zone"
    multi_step_sequence = "multi_step_sequence"
    impossible_task = "impossible_task"


class Bounds(BaseModel):
    x: tuple[float, float]
    y: tuple[float, float]
    z: tuple[float, float]

    @model_validator(mode="after")
    def valid_ranges(self) -> "Bounds":
        for axis in ("x", "y", "z"):
            lo, hi = getattr(self, axis)
            if lo >= hi:
                raise ValueError(f"{axis} bounds must be increasing")
        return self


class Workspace(Bounds):
    pass


class Robot(BaseModel):
    type: str = "arm_6dof"
    workspace: Workspace
    gripper: bool = True
    max_speed: float = Field(default=0.35, gt=0)


class ObjectSpec(BaseModel):
    name: str
    type: str
    position: tuple[float, float, float]
    size: tuple[float, float, float] | None = None
    movable: bool = True
    color: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class Zone(BaseModel):
    name: str
    type: str
    bounds: Bounds


class Scene(BaseModel):
    objects: list[ObjectSpec] = Field(default_factory=list)
    zones: list[Zone] = Field(default_factory=list)


class TaskMetadata(BaseModel):
    generator_version: str
    seed: int | None = None
    is_solvable: bool = True
    explanation: str | None = None
    tags: list[str] = Field(default_factory=list)


class RobotTask(BaseModel):
    id: str
    instruction: str
    scene: Scene
    robot: Robot
    objects: list[ObjectSpec] = Field(default_factory=list)
    zones: list[Zone] = Field(default_factory=list)
    constraints: list[str]
    expected_plan: list[str]
    safety_checks: list[str]
    difficulty: Difficulty
    task_type: TaskType
    metadata: TaskMetadata

    @model_validator(mode="after")
    def validate_task(self) -> "RobotTask":
        if self.objects != self.scene.objects:
            self.objects = self.scene.objects
        if self.zones != self.scene.zones:
            self.zones = self.scene.zones
        if self.metadata.is_solvable and not self.expected_plan:
            raise ValueError("solvable tasks must include a non-empty expected plan")
        if not self.metadata.is_solvable and not self.metadata.explanation:
            raise ValueError("impossible tasks must include an explanation")
        if self.difficulty == Difficulty.impossible and self.metadata.is_solvable:
            raise ValueError("impossible difficulty must be marked unsolvable")
        return self

