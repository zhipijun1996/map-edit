from pathlib import Path
from .approved_author_v1 import purpose
from . import approved_r03_v1 as previous
RUNNER_SCRIPT=Path(__file__).parent/'runtime/repair_runner_v3.gd'
SOURCE_DEPENDENCIES=[*previous.SOURCE_DEPENDENCIES,Path(previous.__file__),Path(__file__).parent/'approved_author_v1.py']
