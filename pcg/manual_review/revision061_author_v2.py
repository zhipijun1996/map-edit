from pathlib import Path
from .revision061_author_v1 import purpose,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/revision061_runner_v2.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('revision061_content_v2.py')]
