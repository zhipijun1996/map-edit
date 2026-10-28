from pathlib import Path
from importlib import import_module
_original=import_module('pcg.migration.foundry_feedback_v5')
purpose=_original.purpose
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[]),Path(__file__).parent.parent/"boundary_runtime_extended.py"]
RUNNER_SCRIPT=Path(__file__).with_name('runner_6a88b78c46c159b9.gd')
