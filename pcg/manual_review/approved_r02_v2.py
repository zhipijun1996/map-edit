from pathlib import Path
from .approved_author_v1 import purpose
from . import approved_r02_v1 as previous
RUNNER_SCRIPT=Path(__file__).parent/'runtime/first30_runner_v2.gd'
SOURCE_DEPENDENCIES=[*previous.SOURCE_DEPENDENCIES,Path(previous.__file__),Path(__file__).parent/'approved_author_v1.py']
