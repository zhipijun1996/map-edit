from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.forest_feedback_v7')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_ce052b8e7cd6ad5d.gd')
