"""Task generator registry."""

from rgen.generators.avoid_zone import AvoidZoneGenerator
from rgen.generators.base import BaseGenerator, GenerationContext
from rgen.generators.impossible import ImpossibleTaskGenerator
from rgen.generators.pick_place import PickAndPlaceGenerator
from rgen.generators.reach import ReachTargetGenerator
from rgen.generators.sequence import MultiStepSequenceGenerator
from rgen.generators.sort import SortObjectsGenerator

GENERATORS: dict[str, type[BaseGenerator]] = {
    "reach_target": ReachTargetGenerator,
    "pick_and_place": PickAndPlaceGenerator,
    "sort_objects": SortObjectsGenerator,
    "avoid_zone": AvoidZoneGenerator,
    "multi_step_sequence": MultiStepSequenceGenerator,
    "impossible_task": ImpossibleTaskGenerator,
}

__all__ = ["BaseGenerator", "GenerationContext", "GENERATORS"]

