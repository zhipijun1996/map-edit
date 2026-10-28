from pathlib import Path
from importlib import import_module
_original=import_module('pcg.prototype.creative_batches.jump_wall.production-v3')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[])]
RUNNER_SCRIPT=Path(__file__).with_name('runner_171837c5699f7a4e.gd')
