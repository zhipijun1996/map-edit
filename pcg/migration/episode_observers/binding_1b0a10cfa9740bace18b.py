from pathlib import Path
from importlib import import_module
from pcg.migration.causal_observer_v2 import correct
_original=import_module('pcg.prototype.workshop.macro')
RUNNER_SCRIPT=Path(__file__).resolve().parents[3]/'pcg/prototype/workshop/runner.gd'
SOURCE_DEPENDENCIES=[Path(_original.__file__),*getattr(_original,"SOURCE_DEPENDENCIES",[]),Path(__file__).parents[1]/"causal_observer_v2.py"]
def purpose(case,raw):
    return correct(case,raw,_original.purpose(case,raw),assertion_source='pcg/prototype/workshop/macro.py')
