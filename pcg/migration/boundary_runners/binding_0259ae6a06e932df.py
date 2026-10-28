from pathlib import Path
from importlib import import_module
_original=import_module('pcg.prototype.workshop.evaluate')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_d05abd8a7b18173c.gd')
