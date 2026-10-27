from pathlib import Path
from importlib import import_module
_original=import_module('pcg.prototype.creative_batches.batch30_d05.api_v2')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_suffix(".gd")
