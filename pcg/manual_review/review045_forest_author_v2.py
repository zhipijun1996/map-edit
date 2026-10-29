from pathlib import Path
from .review045_forest_author_v1 import purpose
from pcg.migration import region_outcomes
RUNNER_SCRIPT=Path(__file__).parent/'runtime/review045_forest_runner_v2.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name('review045_forest_author_v1.py'),Path(__file__).with_name('first40_author_v2.py'),Path(region_outcomes.__file__)]
