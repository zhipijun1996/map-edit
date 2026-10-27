"""Frozen four-port world with four separately required directed witnesses."""
import copy
from pathlib import Path
from . import rules_v1 as rules
from .counter_policy_v1 import classify
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
COUNTER_CLASSIFIER=classify
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'counter_policy_v1.py',HERE/'control-selection-v1.json',HERE/'proposal-v1.json']
def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['counter_scope_policy']=dict(version=1,nominal_body_ownership_required=True,external_paid_alternatives='Semantic acceptance only if actual same gate top landing/refill already passed; external space UNKNOWN, not internal path certificate')
 return c
def layouts(recipe,interface):return[metadata(c)for c in rules.layouts(recipe,interface)]
def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return[metadata(v)for v in rules.alternatives(c)]
def for_exact_request(spec):
 def canonical(s):
  s=copy.deepcopy(s)
  for k in ['id','budget','map_seed']:s.pop(k,None)
  return s
 if not isinstance(spec,dict)or canonical(spec)!=canonical(layouts(RECIPES[0],0)[0]['map_specification']):
  return dict(status='needs_design',conflicts=[dict(field='full_challenge_specification',reason='Only exact four-port initial-closed timed-gate world with all four low-to-high relations and currency supported')],searched=dict(interfaces=[0],block_size=128,registered_pairs=rules.PAIRS),negotiable=['Exact registered shape and directions','New bounded rule/port/state adaptation with independent verification'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),assembly='UNKNOWN',new_physics_cases=0,production_admitted=False)
