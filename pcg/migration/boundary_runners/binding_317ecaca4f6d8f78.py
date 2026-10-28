from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.resource_feedback_v6')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_b0e3e5ed314afeae.gd')
