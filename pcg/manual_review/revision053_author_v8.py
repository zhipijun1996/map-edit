from pathlib import Path
from .revision053_author_v5 import purpose,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/revision053_runner_v8.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('revision053_author_v5.py')]
