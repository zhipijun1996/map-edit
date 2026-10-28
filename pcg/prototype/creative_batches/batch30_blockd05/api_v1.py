"""Frozen original D05 core with explicit Block-owned terminal adapters."""
import copy
from pathlib import Path
from . import rules_v1 as rules
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE/'proposal-v1.json']

def metadata(c):
 c['native_block_scene']=str(NATIVE_SCENE.relative_to(HERE.parents[3]))
 c['native_scene']='res://prototype/creative_batches/batch30_blockd05/main_v1.tscn'
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return c

def layouts(recipe,interface):return[metadata(c)for c in rules.layouts(recipe,interface)]
def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return[metadata(v)for v in rules.alternatives(c)]

def for_exact_request(spec,interface=0):
 def canonical(s):
  s=copy.deepcopy(s)
  for key in ['id','budget','map_seed']:s.pop(key,None)
  return s
 if interface not in [0,1]or not isinstance(spec,dict)or canonical(spec)!=canonical(layouts(RECIPES[0],interface)[0]['map_specification']):
  return dict(status='needs_design',conflicts=[dict(field='full_challenge_specification',reason='Only registered parked-carrier entry, exact terminal geometry and currency transaction supported; arbitrary phase/reverse/no-reward requests not silently substituted')],searched=dict(interfaces=[0,1],registered_pairs=[['A','B']],block_size=128),negotiable=['exact physical request','new bounded registered adaptation and independent physics'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],interface),assembly='UNKNOWN',new_physics_cases=0,production_admitted=False)
