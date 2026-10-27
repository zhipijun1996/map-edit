"""Human A1 two-space bidirectional candidates, current actual Map pair need."""
import copy,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=rules.RECIPES;RUNNER_SCRIPT=rules.RUNNER_SCRIPT;NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE/'control-selection-v1.json',HERE/'required-pairs-v1.json']
CONTROL=json.loads((HERE/'control-selection-v1.json').read_text())['controls']
INPUT=json.loads((HERE/'map-input-v1.json').read_text())
PAIRS=json.loads((HERE/'required-pairs-v1.json').read_text())
assert PAIRS['required_local_pairs']==[['A','B'],['B','A']]

def candidate_for_request(spec,interface=0):
 if interface not in [0,1]:return dict(status='needs_design',conflicts=[dict(field='interface',reason='onlytwooriginalhumanA1spacesregistered')],new_physics_cases=0,production_admitted=False)
 cases=[rules.candidate(interface,CONTROL[f'{interface}/{s}'],s)for s in ['outbound','return']]
 if not isinstance(spec,dict):return dict(status='needs_design',conflicts=[dict(field='request',reason='objectrequired')],new_physics_cases=0)
 if spec.get('rewards')==[]:
  return dict(status='needs_design',conflicts=[dict(field='rewards',reason='RegisteredhumanA1preservesvisible8coin chest; no-rewardtraversal wouldremovehumanmotivation andneedsseparatelydeclaredrevision')],searched=dict(interfaces=[0,1],current_currency=8,ordered_pairs=PAIRS['required_local_pairs']),negotiable=['Explicitriskreward demandwithcurrency allocation','Separatelydeclaredno-rewardvariation withhumanmotivationgap, freshversion/evidence'],new_physics_cases=0,may_delete_required_relations=False,production_admitted=False)
 matches_actual=digest(spec)==digest(INPUT['request']);matches_derived=digest(spec)==digest(cases[0]['map_specification'])
 if not matches_actual and not matches_derived:return dict(status='needs_design',conflicts=[dict(field='request',reason='Outsideexactregisteredr3currency/paircontext orderivedA1riskrewarddemand; noarbitraryrole/port/state substitution')],searched=dict(interfaces=[0,1],current_actual_Map_request=INPUT['request']['id'],ordered_pairs=PAIRS['required_local_pairs'],port_profiles=['ground64/v1']),negotiable=['Newdirection/state/port proof','Originaltwo-space riskreward demand','JointMapresponsibility mapping'],new_physics_cases=0,production_admitted=False)
 response=dict(status='candidate_for_joint_mapping',request_id=spec['id'],source_request_sha256=digest(spec),request_origin='Actual6cMapr3currency+bidirectionalgraphpair context'if matches_actual else'ExplicitderivedhumanA1riskrewarddemand',
  actual_Map_context=INPUT['request']['id'],required_graph_pairs=PAIRS['required_edge_pairs'],proposed_edge_to_port=PAIRS['proposed_edge_to_port'],registered_ordered_pairs=PAIRS['required_local_pairs'],
  role_interpretation=INPUT['role_interpretation'],currency_allocation_proposal=dict(id='allocation-12',kind='currency',amount=8,source_value=INPUT['request']['rewards'][0]['value'],status='proposal_requiresMapbudgetbinding',human_visible_chest_preserved=True),
  unresolved=['Actualcurrencyvalue/allocationbudget','Jointspatialassignmenttoe6/e7','Junctioningress/state interpretation','Arbitraryclaimedchest/ingressresources','Boundarycrossing','Regionalreturncomposition','FullMap'],map_added_terrain=0,may_delete_required_relations=False,production_admitted=False)
 for c in cases:
  c['source_map_request']=copy.deepcopy(spec);c['actual_Map_context']=copy.deepcopy(INPUT['request']);c['map_request_response']=copy.deepcopy(response)
  c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return dict(status='candidate_for_joint_mapping',cases=cases,response=response)

def layouts(recipe,interface):
 if recipe!=RECIPES[0]or interface not in [0,1]:raise ValueError('needs_design: registeredhumanA1twospace only')
 return candidate_for_request(INPUT['request'],interface)['cases']

purpose=rules.purpose
