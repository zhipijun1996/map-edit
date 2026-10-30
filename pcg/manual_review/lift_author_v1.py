from pathlib import Path
from .ideas_author_v2 import purpose,SOURCE_DEPENDENCIES as previous
RUNNER_SCRIPT=Path(__file__).parent/'runtime/lift_runner_v1.gd'
SOURCE_DEPENDENCIES=[*previous,Path(__file__).with_name('ideas_author_v2.py'),Path(__file__).with_name('lift_idea_v1.py')]
