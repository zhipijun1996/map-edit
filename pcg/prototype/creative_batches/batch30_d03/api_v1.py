"""Frozen final D03 adapter, two exact interfaces and all seven route witnesses.

No full calibration, holdout or library admission is implied by probe success.
"""
from pathlib import Path
from .rules_v8 import RECIPES,layouts,purpose,alternatives,depleted_comparisons
from .rules_v8 import SOURCE_DEPENDENCIES as RULE_DEPENDENCIES
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[HERE/'rules_v8.py',*RULE_DEPENDENCIES]
NATIVE_SCENE='res://prototype/creative_batches/batch30_d03/main_v1.tscn'
