from pathlib import Path
from .ideas_author_v1 import purpose,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/ideas_runner_v2.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('ideas_author_v1.py'),Path(__file__).with_name('revision058_content_v1.py')]
