from pathlib import Path
from importlib import import_module
original=import_module('pcg.migration.compat_runners.runner_18bcffac97cd')
purpose=original.purpose
SOURCE_DEPENDENCIES=[Path(original.__file__),*getattr(original,"SOURCE_DEPENDENCIES",[]),Path(__file__).with_name("air_enemy_binding_v1.gd")]
RUNNER_SCRIPT=Path(__file__).with_name('r03_runner_v1.gd')
