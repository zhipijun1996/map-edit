"""Frozen D03 r3 API: same-world raised3HP enemy and angular landing margins.

Full regular calibration/holdout and candidate admission remain root-owned.
Exactly28counter programs per exact route, including realperch/resource cases.
"""
from pathlib import Path
from .rules_v2 import RECIPES,layouts,purpose
from .rules_v2 import SOURCE_DEPENDENCIES as RULE_DEPENDENCIES
from .counter_recipes_v1 import alternatives,depleted_comparisons
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[HERE/'rules_v2.py',HERE/'counter_recipes_v1.py',*RULE_DEPENDENCIES,HERE/'remaining-protocol-v1.json',HERE.parent/'batch30_d03/main_v1.gd',HERE.parent/'batch30_d03/main_v1.tscn']
NATIVE_SCENE='res://prototype/creative_batches/batch30_d03/main_v1.tscn'
