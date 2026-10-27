"""Both actual canonical A->B witnesses are required for this content."""
import copy
from pathlib import Path
from . import rules_v2 as rules
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/main_block_v1.gd',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE/'control-selection-v1.json',HERE/'proposal-v1.json']

def metadata(c):
 c['native_block_scene']=str(NATIVE_SCENE.relative_to(HERE.parents[3]))
 c['native_scene']='res://prototype/creative_batches/batch30_blockc10/main_v1.tscn'
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return c

def layouts(recipe,interface):return[metadata(c)for c in rules.layouts(recipe,interface)]
def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return[metadata(v)for v in rules.alternatives(c)]

def for_exact_request(spec):
 def canonical(s):
  s=copy.deepcopy(s)
  for key in ['id','budget','map_seed']:s.pop(key,None)
  return s
 if not isinstance(spec,dict)or canonical(spec)!=canonical(layouts(RECIPES[0],0)[0]['map_specification']):
  return dict(status='needs_design',conflicts=[dict(field='full_challenge_specification',reason='Only registered two-port under-pocket layout with BOTH nominal and actual miss/restore/A-dock/retry witnesses; extra states, reverse, shape or reward constraints not substituted')],searched=dict(interfaces=[0],block_size=128,canonical_routes=['nominal','miss-restore-retry']),negotiable=['exact physical request','separate bounded new rule and full verification'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),assembly='UNKNOWN',new_physics_cases=0,production_admitted=False)
