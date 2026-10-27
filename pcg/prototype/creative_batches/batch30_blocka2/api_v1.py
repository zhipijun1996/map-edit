"""One fully requested two-direction Block interface; second demand rejected."""
import copy
from pathlib import Path
from . import rules_v2 as rules,counters_v1 as counters
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(counters.__file__),HERE/'control-selection-v2.json',HERE/'main_v1.gd',HERE/'main_v1.tscn',HERE.parent/'batch30_runtime/block_draw_v1.gd',HERE.parents[2]/'creative-production/batch30/map-constraint-source-v2/source-index.json']

def metadata(c):
 c['native_block_scene']=str(NATIVE_SCENE.relative_to(HERE.parents[3]));c['native_scene']='res://prototype/creative_batches/batch30_blocka2/main_v1.tscn'
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]));c['generation_rule']['source_map_contract']='6c864ae6423b6409990564371aca34a322b66253'
 c['scope_limits']=dict(boundary_crossing='UNKNOWN',same_world_foldback='one clean exact floor-return fixture only; noise/full/Map foldback UNKNOWN',arbitrary_carrier_phase='UNKNOWN',reverse_mechanism='Cold parked original carrier landing then ordinary jump; no start/pause necessity on reverse',map_integration='Requires B dynamic carrier Cell consumer and exact directional/state compatibility')
 return c

def layouts(recipe,interface):
 if interface!=0:raise ValueError('needs_design: i1 reverse mild1/3 moderate1/3, fixed two rules exhausted')
 return[metadata(c)for c in rules.layouts(recipe,interface)]

def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return[metadata(v)for v in counters.alternatives(c)]

def for_exact_request(spec,interface=0):
 expected=rules.candidate(0)['map_specification']
 if interface!=0 or not isinstance(spec,dict)or spec!=expected:
  return dict(status='needs_design',conflicts=[dict(field='exact_request_and_bidirectional_interface',reason='Only fully resolved exp0_0 interface0 fresh initial parked world eligible; interface1 reverse fails noise, unbound topology/phase/foldback cannot substitute')],searched=dict(interfaces=[0,1],rule_revisions=2,probe_cases=53,registered_pairs=[['A','B'],['B','A']]),negotiable=['New bounded physical/control proposal','Exact interface0 staging; same-world foldback requires separate evidence'],production_admitted=False)
 return dict(status='requires_physics',cases=layouts(RECIPES[0],0),whole_map='UNKNOWN',foldback='UNKNOWN beyond exact clean fixture',production_admitted=False)
