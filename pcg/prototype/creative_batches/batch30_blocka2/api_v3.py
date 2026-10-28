"""Resolve Map UNKNOWN fields explicitly for original Module store consumers.

Raw Map input and its unsatisfied global foldback remain separately bound.
No physical entity, controller, initial state or original evidence is changed.
"""
import copy,json
from pathlib import Path
from . import api_v2 as previous
HERE=Path(__file__).parent
RECIPES=previous.RECIPES;RUNNER_SCRIPT=previous.RUNNER_SCRIPT;NATIVE_SCENE=previous.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(previous.__file__),*previous.SOURCE_DEPENDENCIES,HERE/'metadata-repair-protocol-v2.json']
ORIGINAL=json.loads((HERE/'source-map-demand-v1.json').read_text())['original_request']


def metadata(case):
    case=previous.metadata(case)
    spec=copy.deepcopy(case['map_specification'])
    grid=case['block_grid'];size=grid['size'];cells=grid['cells']
    width=(max(x for x,y in cells)-min(x for x,y in cells)+1)*size
    height=(max(y for x,y in cells)-min(y for x,y in cells)+1)*size
    spec['id']=ORIGINAL['id']+'/resolved-local-A2/0'
    spec['relations']=[dict(from_port=a,to_port=b,role='main'if a=='A'else'return')for a,b in [('A','B'),('B','A')]]
    spec['ports']['required_normals']=[p['normal']for p in case['ports']]
    spec['space']=dict(block_size=size,max_width=width,max_height=height,max_port_span_x=abs(case['ports'][1]['position'][0]-case['ports'][0]['position'][0]),port_profiles=['ground64/v1'])
    spec['capabilities']['allOf']=case['capabilities'][:]
    spec['objective'].update(interface=0,physical_layout_sha256=case['layout_uid'],source_Map_request=ORIGINAL['id'],base_locomotion_bridge='move is implicit base movement in the original graph, not a new unlock')
    spec['risk_reward']=dict(mandatory_damage=False,reward_sites=[])
    case['map_specification']=spec
    case['source_map_request']=copy.deepcopy(ORIGINAL)
    case['map_request_response']=dict(status='candidate_for_joint_mapping',request_id=ORIGINAL['id'],registered_ordered_pairs=[['A','B'],['B','A']],resolved_local_bounds=[width,height],map_added_terrain=0,raw_Map_input_preserved=True,full_Map_foldback='UNKNOWN; one exact clean same-world fixture is not a regional return proof',unresolved=['Joint Port-edge/spatial assignment','Arbitrary ingress and carrier phase','Boundary crossing','Original expedition foldback condition','Full Map'],production_admitted=False)
    case['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
    return case


def layouts(recipe,interface):return[metadata(c)for c in previous.layouts(recipe,interface)]
def alternatives(case):return[metadata(c)for c in previous.alternatives(case)]
purpose=previous.purpose


def for_exact_request(spec,interface=0):
    if interface!=0:return previous.for_exact_request(spec,interface)
    cases=layouts(RECIPES[0],0)
    if spec!=ORIGINAL and spec!=cases[0]['map_specification']:
        return dict(status='needs_design',conflicts=[dict(field='exact_Map_or_resolved_local_request',reason='Only pinned original exp0_0 or its explicit bounded A2 local compilation supported')],new_physics_cases=0,production_admitted=False)
    return dict(status='requires_physics',cases=cases,response=cases[0]['map_request_response'])
