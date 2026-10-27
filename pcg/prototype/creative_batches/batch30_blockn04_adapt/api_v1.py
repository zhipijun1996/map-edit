"""One asymmetric three-port demand, original gate-return action family."""
import copy
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.creative_batches.batch30_blockn04.counter_policy_v1 import classify
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
COUNTER_CLASSIFIER=classify
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'control-selection-v1.json',HERE/'proposal-v1.json',HERE.parents[2]/'map_directed/block_grid/contracts.py',HERE.parents[2]/'creative-production/batch30/map-constraint-source-v2/source-index.json']
def metadata(c):
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 c['counter_scope_policy']=dict(version=1,nominal_body_ownership_required=True,external_paid_alternatives='Only actually demonstrated same-gate top landing/refill with extra paid gun can be causally accepted; outside air remains spatialUNKNOWN. A cheaper skip-gate route is not accepted.')
 return c
def layouts(recipe,interface):return[metadata(c)for c in rules.layouts(recipe,interface)]
def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return[metadata(v)for v in rules.alternatives(c)]
def for_exact_request(spec):
 def canonical(s):
  s=copy.deepcopy(s)
  for k in ['id','budget','map_seed']:s.pop(k,None)
  return s
 supported=layouts(RECIPES[0],1)[0]['map_specification']
 if not isinstance(spec,dict)or canonical(spec)!=canonical(supported):
  return dict(status='needs_design',conflicts=[dict(field='full_challenge_specification',reason='Exact new three-port asymmetric fork only; original four-port interchangeable layout, opposite directions, rewards, state or size changes require fresh generation/verification')],searched=dict(interfaces=[1],block_size=128,registered_pairs=[['A','B'],['A','C']]),negotiable=['Exact concrete three-port demand','Independent new rule/state/port adaptation'],new_physics_cases=0,production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],1),assembly='UNKNOWN',new_physics_cases=0,production_admitted=False)
