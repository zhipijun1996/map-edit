from pathlib import Path
from .review045_forest_author_v2 import purpose,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/revision053_forest_runner_v1.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('review045_forest_author_v2.py')]
