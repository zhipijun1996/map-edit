from pathlib import Path
from .ideas_author_v5 import purpose,SOURCE_DEPENDENCIES as previous
RUNNER_SCRIPT=Path(__file__).parent/'runtime/ideas_runner_v6.gd'
SOURCE_DEPENDENCIES=[*previous,Path(__file__).with_name('ideas_author_v5.py')]
