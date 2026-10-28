from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.forest_region_drop_v15')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_525365cbdc68916e.gd')
