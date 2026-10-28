from pathlib import Path
from importlib import import_module
original=import_module('pcg.prototype.creative_batches.batch30_blockn06_fourport.api_v1')
purpose=original.purpose
SOURCE_DEPENDENCIES=[Path(original.__file__),*getattr(original,"SOURCE_DEPENDENCIES",[]),Path(__file__).with_name("air_enemy_binding_v1.gd")]
RUNNER_SCRIPT=Path(__file__).with_name('r01_runner_v1.gd')
