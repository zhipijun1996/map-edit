from pathlib import Path
from .lift_author_v1 import purpose,SOURCE_DEPENDENCIES as previous
RUNNER_SCRIPT=Path(__file__).parent/'runtime/lift_runner_v2.gd'
SOURCE_DEPENDENCIES=[*previous,Path(__file__).with_name('lift_author_v1.py')]
