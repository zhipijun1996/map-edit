"""Single exact three-port new Block station recipe; all other pairs UNKNOWN."""
import copy,json
from pathlib import Path
from . import rules_v2 as rules
from .alternatives_v1 import alternatives
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE.parent/'batch30_c05/alternatives_v1.py',HERE/'control-selection-v2.json']
CONTROL=json.loads((HERE/'control-selection-v2.json').read_text())['controls']

def candidate_for_request(spec,interface=0):
 if interface!=0:return dict(status='needs_design',conflicts=[dict(field='interface',reason='old_highcourt_near_branch_failed; only_wide_newrule_registered')],new_physics_cases=0,production_admitted=False)
 cases=[rules.candidate(0,CONTROL[route],route)for route in ['near','far']];expected=cases[0]['map_specification']
 if not isinstance(spec,dict)or digest(spec)!=digest(expected):
  return dict(status='needs_design',conflicts=[dict(field='request',reason='only_exact_derived_threeport_fork_registered; no_Bgraph_or_arbitrary_ports_rewards_reverse_substitution')],searched=dict(interfaces=[0],port_normals=[[-1,0],[-1,0],[1,0]],ordered_pairs=[['A','B'],['A','C']],size=128),negotiable=['explicit_new_geometry_and_full_verification','independent_reverse_and_boundary_crossing_evidence','actual_B_junction_demand_joint_assignment'],new_physics_cases=0,production_admitted=False)
 response=dict(status='candidate_for_joint_mapping',request_id=spec['id'],source_request_sha256=digest(spec),request_origin='TaskA_derived_current_Map_contract; not_actual_Bgraph_request',registered_ordered_pairs=[['A','B'],['A','C']],unresolved=['Bgraph_joint_assignment','B_to_A','B_to_C','C_to_A','C_to_B','arbitrary_ingress','boundary_crossing','continuous_external_state_transfer','full_Map'],map_added_terrain=0,reward_budget='Only_real_10coin_near_and16coin_far_chests; no_major_item_service',production_admitted=False)
 for c in cases:
  c['source_map_request']=copy.deepcopy(spec);c['map_request_response']=copy.deepcopy(response)
  c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return dict(status='candidate_for_joint_mapping',cases=cases,response=response)

def layouts(recipe,interface):
 if recipe!=RECIPES[0]:raise ValueError('unsupported_BlockC05_recipe')
 if interface!=0:raise ValueError('needs_design: unsupported secondspace; oldhighcourt near failed')
 request=rules.candidate(0,CONTROL['near'],'near')['map_specification'];return candidate_for_request(request,0)['cases']

purpose=rules.purpose
