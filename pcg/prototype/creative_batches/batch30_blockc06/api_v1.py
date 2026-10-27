"""Frozen registration: one true three-port world, two explicit directions."""
import copy
from pathlib import Path
from . import rules_v2 as rules
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'proposal-v1.json',HERE/'screen-interpretation-v1.json']

def layouts(recipe,interface):
 cases=rules.layouts(recipe,interface)
 for c in cases:c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return cases

def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return rules.alternatives(c)

def for_exact_request(spec):
 """Do not claim arbitrary Map requests are this physical fork."""
 supported=layouts(RECIPES[0],0)[0]['map_specification']
 def semantic(s):
  s=copy.deepcopy(s)
  for k in ['id','budget','map_seed']:s.pop(k,None)
  return s
 if not isinstance(spec,dict)or semantic(spec)!=semantic(supported):
  return dict(status='needs_design',conflicts=[dict(field='full_challenge_specification',reason='Only the registered exact three-port physical fork is supported; no silent reward/return/port/state substitution')],searched=dict(recipe=RECIPES[0],interfaces=[0],block_size=128,registered_pairs=[['A','B'],['A','C']]),negotiable=['exact published physical request','new bounded registered adaptation with fresh evidence'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),assembly='UNKNOWN',new_physics_cases=0,production_admitted=False)
