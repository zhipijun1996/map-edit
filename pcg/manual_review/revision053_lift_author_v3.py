from pathlib import Path
from .revision053_three_author_v2 import purpose,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/revision053_lift_runner_v2.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('revision053_three_author_v2.py')]
