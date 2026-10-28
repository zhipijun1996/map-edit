"""D03 r2 frozen rule: body-safe early takeoff and wider east receiver.
Full regular calibration/holdout remains root-owned and NOT_RUN here.
"""
from pathlib import Path
from .rules_v1 import RECIPES,layouts,purpose,alternatives,depleted_comparisons
from .rules_v1 import SOURCE_DEPENDENCIES as RULE_DEPENDENCIES
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[HERE/'rules_v1.py',*RULE_DEPENDENCIES,HERE/'remaining-protocol-v1.json',HERE.parent/'batch30_d03/main_v1.gd',HERE.parent/'batch30_d03/main_v1.tscn']
NATIVE_SCENE='res://prototype/creative_batches/batch30_d03/main_v1.tscn'
