"""Frozen final C03 side-grotto registration and honest validation consumers."""
import copy
from pathlib import Path
from . import api_v1 as prior
from .validation_v7 import dead_fixture
from .validation_v5 import guard_fixture
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,*[HERE/n for n in ['probe-receipt-v1.json','validation_v7.py','validation_v6.py','validation_v5.py','repair_v4.py','verification-protocol-v3.json','verification-protocol-v4.json','verification-protocol-v5.json']]]
purpose=prior.purpose
alternatives=prior.alternatives
required_world_outcome=prior.required_world_outcome
def layouts(recipe,interface):
 cases=prior.layouts(recipe,interface);spec=copy.deepcopy(cases[0]['map_specification'])
 spec['return_conditions']='Exact validation-only actual air-reward-returnA guard passed clean; real3HP-dead->staged passed clean+2mild. These are small witnesses, not full regular return/holdout. General B->A,seams and arbitrary states UNKNOWN.'
 for c in cases:
  c['map_specification']=spec;c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return cases
