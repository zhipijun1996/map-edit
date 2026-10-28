from pathlib import Path
from pcg.manual_review.review_refresh_author_v1 import purpose
RUNNER_SCRIPT=Path('pcg/manual_review/runtime/first40_resource_fixture_v2.gd').resolve()
SOURCE_DEPENDENCIES=[Path(__file__).with_name('review_refresh_author_v1.py'),Path(__file__).with_name('first40_author_v2.py')]
