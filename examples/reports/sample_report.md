# RGen Dataset Report

Dataset path: `examples\datasets\sample_tasks.jsonl`

### Summary

| Metric | Value |
| --- | ---: |
| Total tasks | 15 |
| Solvable tasks | 12 |
| Impossible tasks | 3 |
| Average plan length | 7.53 |
| Average objects | 2.87 |
| Average constraints | 3.73 |
| Average zones | 0.60 |

### Task Type Distribution

| Metric | Value |
| --- | ---: |
| avoid_zone | 1 |
| impossible_task | 3 |
| multi_step_sequence | 2 |
| pick_and_place | 2 |
| reach_target | 3 |
| spatial_relation | 4 |

### Difficulty Distribution

| Metric | Value |
| --- | ---: |
| easy | 5 |
| hard | 4 |
| impossible | 3 |
| medium | 3 |

### Ambiguity Distribution

| Metric | Value |
| --- | ---: |
| explicit | 7 |
| mild_ambiguous | 7 |
| underspecified | 1 |

### Failure Mode Distribution

| Metric | Value |
| --- | ---: |
| ambiguous_without_resolution | 1 |
| conflicting_constraints | 1 |
| no_matching_container | 1 |

### Most Common Constraints

| Metric | Value |
| --- | ---: |
| avoid forbidden zones | 7 |
| complete requested manipulation | 3 |
| complete subtasks in order | 2 |
| drawer must be closed after placement | 2 |
| drawer must be open before placing object inside | 2 |
| grasp selected object before transport | 4 |
| maintain controlled speed | 3 |
| object must be grasped before transport | 2 |
| resolve spatial reference before motion | 4 |
| respect workspace bounds | 15 |

### Most Common Safety Checks

| Metric | Value |
| --- | ---: |
| clearance_check | 1 |
| forbidden_zone_check | 11 |
| gripper_state_check | 8 |
| object_attachment_check | 2 |
| ordered_subtask_check | 2 |
| resolved_reference_check | 4 |
| solvability_check | 3 |
| speed_limit_check | 3 |
| workspace_bounds_check | 15 |

### Validation Summary

| Metric | Value |
| --- | ---: |
| Errors | 0 |

### Dataset Quality Warnings

- No validation errors were found.

### Recommended Use Cases

- LLM robot planner evaluation
- Spatial-reference reasoning benchmarks
- Safety-checking and rejection behavior tests
- Curriculum generation from easy to hard symbolic tasks

### Example Tasks

#### rgen_000001

- Type: `reach_target`
- Difficulty: `easy`
- Ambiguity: `explicit`
- Instruction: Move the robot end effector to target position (-0.303, -0.334, 0.25) while respecting all constraints.
- Plan length: 5

#### rgen_000002

- Type: `multi_step_sequence`
- Difficulty: `easy`
- Ambiguity: `explicit`
- Instruction: Open the drawer, place the red cube inside it, then close the drawer.
- Plan length: 9

#### rgen_000003

- Type: `spatial_relation`
- Difficulty: `medium`
- Ambiguity: `mild_ambiguous`
- Instruction: Move the rightmost movable cube into the green_tray without entering the restricted zone.
- Plan length: 9

#### rgen_000004

- Type: `reach_target`
- Difficulty: `hard`
- Ambiguity: `mild_ambiguous`
- Instruction: Move the robot end effector to target position (0.044, 0.277, 0.25) while respecting all constraints.
- Plan length: 6

#### rgen_000005

- Type: `multi_step_sequence`
- Difficulty: `hard`
- Ambiguity: `mild_ambiguous`
- Instruction: Open the drawer, place the red cube inside it, then close the drawer.
- Plan length: 9
