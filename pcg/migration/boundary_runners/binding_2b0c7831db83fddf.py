from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.forest_source_approach_v13')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_6be725d40055bbc3.gd')
