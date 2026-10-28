from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.game_search')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_79a86e504ba3e88d.gd')
