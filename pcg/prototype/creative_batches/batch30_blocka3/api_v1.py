"""Frozen A3 two-space, directed pair interface on the actual Map traversal."""
import copy,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE/'control-selection-v1.json']
CONTROL=json.loads((HERE/'control-selection-v1.json').read_text())['controls']
INPUT=json.loads((HERE/'map-input-v1.json').read_text())
PAIRS=json.loads((HERE/'required-pairs-v1.json').read_text())
assert PAIRS['local_pairs']==[['A','B'],['B','A']]

def candidate_for_request(spec,interface=0):
 if interface not in [0,1]or not isinstance(spec,dict):return dict(status='needs_design',conflicts=[dict(field='request/interface',reason='onlytwoexactregisteredA3spaces')],new_physics_cases=0,production_admitted=False)
 cases=[rules.candidate(interface,CONTROL[f'{interface}/{s}'],s)for s in ['outbound','return']]
 actual=digest(spec)==digest(INPUT['request']);derived=digest(spec)==digest(cases[0]['map_specification'])
 if not actual and not derived:return dict(status='needs_design',conflicts=[dict(field='request',reason='Outsideexactactual6cMapexp0_0no-rewardpaircontext or explicitderivedbidirectionalA3traversal')],searched=dict(interfaces=[0,1],ordered_pairs=PAIRS['local_pairs'],port_profiles=['ground64/v1'],rewards=[]),negotiable=['Newport/state/directionproof','Separatelydeclaredrewardvariant withfreshMapbudgetbinding'],new_physics_cases=0,production_admitted=False)
 response=dict(status='candidate_for_joint_mapping',request_id=spec['id'],source_request_sha256=digest(spec),actual_Map_context=INPUT['request']['id'],required_graph_pairs=PAIRS['edge_pairs'],proposed_edge_to_port=INPUT['edge_to_port'],registered_ordered_pairs=PAIRS['local_pairs'],explicit_Map_no_reward_variant=True,original_human_A3_requires_chest=False,map_added_terrain=0,may_delete_required_relations=False,production_admitted=False,unresolved=['Jointspatialassignmenttoe23/e24','Arbitraryingressresources/gatephase','Boundarycrossing','Regionalreturncomposition','FullMap'])
 for c in cases:
  c['source_map_request']=copy.deepcopy(spec);c['actual_Map_context']=copy.deepcopy(INPUT['request']);c['map_request_response']=copy.deepcopy(response)
  c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return dict(status='candidate_for_joint_mapping',cases=cases,response=response)

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface not in [0,1]:raise ValueError('needs_design: registeredhumanA3twospaces only')
 return candidate_for_request(INPUT['request'],interface)['cases']

purpose=rules.purpose
