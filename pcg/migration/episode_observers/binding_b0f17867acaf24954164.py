from pathlib import Path
from importlib import import_module
from pcg.migration.causal_observer_v2 import correct
_original=import_module('pcg.migration.boundary_runners.runner_ec80313ee74b84f5')
RUNNER_SCRIPT=Path(__file__).resolve().parents[3]/'pcg/migration/boundary_runners/runner_ec80313ee74b84f5.gd'
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[]),Path(__file__).parents[1]/"causal_observer_v2.py"]
def purpose(case,raw):
    return correct(case,raw,_original.purpose(case,raw),assertion_source='pcg/prototype/workshop/macro.py')
