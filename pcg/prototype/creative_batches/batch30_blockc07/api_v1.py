"""Exact C07 horizontal Block candidate, original causal/paid policy classifier."""
import copy,json
from pathlib import Path
from . import rules_v2 as rules
from .alternatives_v1 import alternatives
from .counter_policy_v1 import classify as COUNTER_CLASSIFIER
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE.parent/'batch30_c07/alternatives_v1.py',HERE/'control-selection-v2.json',HERE/'counter_policy_v1.py']
CONTROL=json.loads((HERE/'control-selection-v2.json').read_text())['control']

def candidate_for_request(spec,interface=0):
 if interface!=0:return dict(status='needs_design',conflicts=[dict(field='interface',reason='only_horizontal_registered; original_vertical_exit_failed')],new_physics_cases=0,production_admitted=False)
 c=rules.candidate(0,CONTROL);expected=c['map_specification']
 if not isinstance(spec,dict)or digest(spec)!=digest(expected):return dict(status='needs_design',conflicts=[dict(field='request',reason='only_exact_derived_Block128_collisionbrake_demand_registered; no_arbitrary_Bgraph_reward_or_direction_substitution')],searched=dict(interfaces=[0],ordered_pairs=[['A','B']],size=128,port_normals=[[-1,0],[1,0]]),negotiable=['explicit_new_geometry_and_controls','fresh_regular_and_independentheld','actual_Bgraph_joint_mapping'],new_physics_cases=0,production_admitted=False)
 response=dict(status='candidate_for_joint_mapping',request_id=spec['id'],source_request_sha256=digest(spec),request_origin='TaskA_derived_current_Map_contract; not_actual_Bgraph_request',registered_ordered_pairs=[['A','B']],unresolved=['Bgraph_joint_assignment','arbitrary_entry','reverse','boundary_crossing','rightstairs_recovery_inside_ownership','state_transfer','full_Map'],map_added_terrain=0,reward_budget='Actual12coin_chest_only; no_major_item_service',production_admitted=False)
 c['source_map_request']=copy.deepcopy(spec);c['map_request_response']=response;c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return dict(status='candidate_for_joint_mapping',case=c,response=response)

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface!=0:raise ValueError('needs_design: only_current_horizontal_collisionbrake_registered')
 request=rules.candidate(0,CONTROL)['map_specification'];return[candidate_for_request(request,0)['case']]

purpose=rules.purpose
