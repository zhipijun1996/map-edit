from pathlib import Path
from .ideas_author_v1 import purpose,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/revision059_hq_runner_v1.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('revision059_hq_content_v1.py')]
