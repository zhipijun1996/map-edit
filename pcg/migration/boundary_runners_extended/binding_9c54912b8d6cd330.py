from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.boundary_runners.binding_774191e6c2ae482a')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[]),Path(__file__).parent.parent/"boundary_runtime_extended.py"]
RUNNER_SCRIPT=Path(__file__).with_name('runner_643ef02f5f3f51ac.gd')
