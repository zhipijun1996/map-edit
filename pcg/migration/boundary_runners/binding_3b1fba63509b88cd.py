from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.forest_feedback_v9')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_22d41fd8116f6549.gd')
