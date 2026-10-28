from pathlib import Path
from importlib import import_module
from pcg.migration.causal_observer_v2 import correct
_original=import_module('pcg.migration.boundary_runners.binding_9e0219de63054544')
RUNNER_SCRIPT=Path(__file__).resolve().parents[3]/'pcg/migration/boundary_runners/runner_d05abd8a7b18173c.gd'
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[]),Path(__file__).parents[1]/"causal_observer_v2.py"]
def purpose(case,raw):
    return correct(case,raw,_original.purpose(case,raw),assertion_source='pcg/prototype/workshop/macro.py')
