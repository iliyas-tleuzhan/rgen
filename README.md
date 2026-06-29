# RGen - Synthetic Robot Dataset Generator

RGen is an offline Python toolkit for generating symbolic robotics task datasets for training and evaluating LLM robot planners. It creates structured JSONL, YAML, and CSV outputs with natural-language instructions, robot scenes, spatial references, ambiguity labels, constraints, expected symbolic plans, safety checks, difficulty labels, and intentionally impossible tasks.

This project focuses on planning and reasoning data, not computer vision, teleoperation, or physics simulation.

## Why This Exists

LLM-based robot planners need many structured examples of what a task means, what constraints matter, what safety checks should run, and what a correct plan should look like. Real robot data is expensive, slow to collect, and often too environment-specific. RGen provides a lightweight way to create reproducible symbolic robotics datasets for research, evaluation, and curriculum design.

## Robotics/AI Motivation

Modern robot systems increasingly combine language models with symbolic planners, behavior trees, motion planners, and safety validators. RGen generates the planning-side supervision those systems need: scene state, robot capabilities, object metadata, constraints, safety checks, plan steps, and solvability labels.

## Installation

```bash
python -m pip install -e ".[dev]"
```

RGen requires Python 3.11+ and runs fully offline.

## Quickstart

```bash
rgen generate --n 20 --difficulty mixed --seed 42 --out data/sample.jsonl
rgen validate data/sample.jsonl
rgen stats data/sample.jsonl
rgen report data/sample.jsonl --out data/report.md
rgen sample data/sample.jsonl --n 5
```

## CLI Usage

```bash
rgen generate --n 100 --out data/tasks.jsonl
rgen generate --n 100 --difficulty easy --out data/easy.jsonl
rgen generate --n 100 --difficulty mixed --format yaml --out data/tasks.yaml
rgen validate data/tasks.jsonl
rgen stats data/tasks.jsonl
rgen report data/tasks.jsonl --out data/report.md
rgen sample data/tasks.jsonl --n 5
rgen split data/tasks.jsonl --train 0.8 --val 0.1 --test 0.1 --out-dir data/splits
```

Use `--seed` for deterministic generation:

```bash
rgen generate --n 100 --seed 42 --out data/tasks.jsonl
```

## Example Generated Task

```json
{
  "id": "rgen_000001",
  "instruction": "Move the red_cube into the blue_bin without violating safety constraints.",
  "task_type": "pick_and_place",
  "difficulty": "medium",
  "robot": {
    "type": "arm_6dof",
    "workspace": {"x": [-0.5, 0.5], "y": [-0.5, 0.5], "z": [0.0, 0.8]},
    "gripper": true,
    "max_speed": 0.35
  },
  "scene": {
    "objects": [
      {"name": "red_cube", "type": "cube", "position": [0.2, 0.1, 0.05], "size": [0.04, 0.04, 0.04], "movable": true, "color": "red"},
      {"name": "blue_bin", "type": "container", "position": [-0.2, 0.2, 0.05], "size": [0.14, 0.14, 0.1], "movable": false, "color": "blue"}
    ],
    "zones": []
  },
  "constraints": ["respect workspace bounds", "object must be grasped before transport"],
  "expected_plan": ["validate_scene", "check_workspace_bounds", "plan_path_to_red_cube", "open_gripper", "move_to_grasp", "close_gripper", "place_object", "verify_task_success"],
  "safety_checks": ["workspace_bounds_check", "gripper_state_check", "object_attachment_check"],
  "metadata": {
    "generator_version": "0.2.0",
    "seed": 42,
    "is_solvable": true,
    "explanation": null,
    "ambiguity": "mild_ambiguous",
    "requires_clarification": false,
    "clarification_question": null,
    "failure_mode": null,
    "resolved_references": {"target_object": "red_cube", "target_container": "blue_bin"},
    "tags": ["pick_and_place", "grasping"]
  }
}
```

## New in v0.2

RGen v0.2 adds richer task variation, spatial-relation tasks, ambiguity metadata, impossible-task failure modes, deeper validation, Markdown dataset reports, and committed sample datasets. Generators now vary instruction wording, objects, shapes, containers, forbidden zones, distractors, constraints, plan length, safety checks, and metadata while staying deterministic under a seed.

## Dataset Schema

Each task includes:

- `id`: stable task identifier
- `instruction`: natural-language robot command
- `scene`: symbolic scene with objects and zones
- `robot`: robot type, workspace, gripper, and speed metadata
- `objects`: top-level copy of scene objects for convenient indexing
- `zones`: top-level copy of scene zones for convenient indexing
- `constraints`: symbolic constraints the planner must satisfy
- `expected_plan`: ordered symbolic plan steps
- `safety_checks`: checks that should run before or during execution
- `difficulty`: `easy`, `medium`, `hard`, or `impossible`
- `task_type`: task family
- `metadata`: generator version, seed, solvability flag, explanation, ambiguity, clarification fields, failure mode, resolved references, and tags

## Ambiguity Levels

- `explicit`: all needed objects and constraints are clearly stated.
- `mild_ambiguous`: the instruction uses resolvable references such as `closest object`, `leftmost cube`, or `matching bin`.
- `underspecified`: the instruction lacks a key detail, so a safe planner should ask a clarification or reject direct execution.

Underspecified tasks include `requires_clarification: true` and a `clarification_question`.

## Spatial-Relation Tasks

The `spatial_relation` task type evaluates whether a planner can resolve symbolic spatial references before acting. Examples include closest object to a bin, leftmost movable cube, rightmost cube, and object farthest from a target area. These tasks include deterministic `metadata.resolved_references` such as:

```json
{
  "closest_object_to_blue_bin": "red_cube_1",
  "target_container": "green_tray"
}
```

## Task Types

- `reach_target`: move the robot to a symbolic target
- `pick_and_place`: grasp and move an object into a container or target area
- `sort_objects`: place multiple objects into matching bins
- `avoid_zone`: complete a motion while avoiding restricted areas
- `multi_step_sequence`: complete ordered symbolic subtasks
- `spatial_relation`: resolve a spatial reference before executing a manipulation
- `impossible_task`: generate intentionally unsolvable tasks with explanations

## Impossible Task Failure Modes

Impossible tasks are marked with `is_solvable: false`, a human-readable `explanation`, and a machine-readable `failure_mode`. Supported failure modes include:

- `unreachable_target`
- `missing_required_object`
- `conflicting_constraints`
- `fully_blocked_workspace`
- `no_matching_container`
- `ambiguous_without_resolution`

Impossible tasks use safe rejection plans such as `validate_scene`, `check_solvability`, `detect_unreachable_target`, and `reject_task_with_explanation`.

## Dataset Reports

Use `rgen report` to create a Markdown report summarizing dataset quality:

```bash
rgen generate --n 1000 --difficulty mixed --seed 42 --out data/tasks.jsonl
rgen report data/tasks.jsonl --out data/report.md
```

Reports include task type, difficulty, ambiguity, solvability, failure mode distributions, common constraints, safety checks, validation summaries, quality warnings, and example tasks.

## Example Workflow

```bash
python -m pip install -e ".[dev]"
rgen generate --n 1000 --difficulty mixed --seed 42 --out data/tasks.jsonl
rgen validate data/tasks.jsonl
rgen stats data/tasks.jsonl
rgen report data/tasks.jsonl --out data/report.md
rgen split data/tasks.jsonl --out-dir data/splits
```

## Difficulty Levels

- `easy`: fewer objects, short plans, minimal constraints
- `medium`: added constraints and optional forbidden zones
- `hard`: distractors, longer plans, multiple zones, stricter checks
- `impossible`: unreachable, missing, blocked, or conflicting tasks with `is_solvable: false`

## Use Cases

- LLM robot planner training
- LLM robot command evaluation
- Synthetic robotics benchmark creation
- Safety-checking research
- Curriculum generation

## Demo Video Script

1. Show the repository structure and explain that RGen runs fully offline.
2. Run `python -m pip install -e ".[dev]"`.
3. Generate a deterministic dataset with `rgen generate --n 20 --difficulty mixed --seed 42 --out data/sample.jsonl`.
4. Validate it with `rgen validate data/sample.jsonl`.
5. Show dataset metrics with `rgen stats data/sample.jsonl`.
6. Display examples with `rgen sample data/sample.jsonl --n 5`.
7. Split the dataset with `rgen split data/sample.jsonl --out-dir data/splits`.
8. Open one JSONL row and point out the instruction, scene, constraints, expected plan, safety checks, difficulty, and solvability metadata.

## Roadmap

- Hugging Face dataset export
- DSPy evaluator integration
- ROS 2 behavior tree export
- Symbolic simulator
- LLM planner benchmark

## CV Bullet

Built **RGen**, an offline synthetic robotics dataset generator for LLM robot planning research. The system generates symbolic robot scenes, natural-language instructions, spatial-relation tasks, ambiguity labels, safety constraints, expected plans, impossible-task failure modes, validation reports, and train/validation/test splits for evaluating robot instruction-following models.

## Development

```bash
python -m pip install -e ".[dev]"
pytest
ruff check .
```

## License

MIT
