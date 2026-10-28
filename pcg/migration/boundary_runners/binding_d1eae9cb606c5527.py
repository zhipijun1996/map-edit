from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.forest_hollow_v10')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_73e5e83207b49a21.gd')
