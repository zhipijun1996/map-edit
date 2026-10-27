"""Strict Map-request compiler and production registration for the v2 world."""
import copy
from pathlib import Path
from . import rules_v2 as rules
from . import api_v1 as previous
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),Path(previous.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'request-guard-protocol-v1.json']


def requested_pairs(spec):
    out=[]
    for value in [spec.get('relations'),spec.get('ports',{}).get('required_pairs')]:
        if isinstance(value,list):
            for row in value:
                if isinstance(row,dict):
                    a=row.get('from_port',row.get('from'));b=row.get('to_port',row.get('to'))
                    if a is not None and b is not None:out.append([a,b])
                elif isinstance(row,(list,tuple))and len(row)==2:out.append(list(row))
        elif isinstance(value,dict):
            for a,targets in value.items():
                if isinstance(targets,dict):
                    for b,want in targets.items():
                        if want in [True,'path','required']:out.append([a,b])
    ret=spec.get('return_conditions',{})
    if isinstance(ret,dict):
        if any(ret.get(k)is True for k in ['required','reverse','bidirectional','same_path']):out.append(['B','A'])
        if any(b.get('kind')=='foldback'for b in ret.get('branches',[])if isinstance(b,dict)):out.append(['B','A'])
    if spec.get('ports',{}).get('bidirectional')is True:out.append(['B','A'])
    return [list(p)for p in dict.fromkeys(tuple(p)for p in out)]


def candidate_for_request(spec,interface=0,control=0):
    conflicts=[];verification=[]
    def conflict(field,reason,**kwargs):conflicts.append(dict(field=field,reason=reason,**kwargs))
    if not isinstance(spec,dict):return dict(status='needs_design',conflicts=[dict(field='request',reason='object_required')],production_admitted=False)
    if spec.get('schema')!='map-notes/challenge-specification/v1':conflict('schema','unsupported_challenge_schema')
    if spec.get('region')!='plains':conflict('region','only_plains_registered')
    if spec.get('objective',{}).get('roles')!=['traversal']:conflict('objective.roles','only_actual_traversal_recipe; boss/junction/service not substituted')
    block=spec.get('block_grid',{})
    if type(block.get('size'))is not int or block.get('size')!=128:conflict('block_grid.size','only_128_registered')
    if type(block.get('map_added_terrain'))is not int or block.get('map_added_terrain')!=0:conflict('block_grid.map_added_terrain','must_explicitly_require_zero')
    if block.get('shape')not in [None,'connected_polyomino']:conflict('block_grid.shape','unsupported_shape_request')
    if block.get('port_anchors')not in [None,'boundary_cell_centers']:conflict('block_grid.port_anchors','boundary_cell_centers_required')
    ports=spec.get('ports',{})
    if type(ports.get('count'))is not int or ports.get('count')!=2:conflict('ports.count','exact_two_physical_ports_supported')
    normals=ports.get('required_normals')
    if normals is not None and normals!=[[-1,0],[1,0]]:conflict('ports.required_normals','only_W_A_to_E_B_is_registered')
    caps=spec.get('capabilities',{})
    if caps.get('status')!='defined':conflict('capabilities.status','unknown_available_capabilities_do_not_satisfy_recipe')
    allowed=caps.get('allOf',[])
    if not isinstance(allowed,list)or not all(isinstance(k,str)for k in allowed):conflict('capabilities.allOf','explicit_capability_list_required');allowed=[]
    if not {'jump','shot_recoil'}<=set(allowed):conflict('capabilities.allOf','jump_and_shot_recoil_required')
    if not set(allowed)<={'move','jump','shot_recoil'}:conflict('capabilities.allOf','unsupported_additional_capability')
    if caps.get('anyOfGroups'):conflict('capabilities.anyOfGroups','unregistered_groups_cannot_be_assumed')
    if spec.get('rewards')!=[]:conflict('rewards','only_explicit_no_reward_request_compiled; currency_not_major_item')
    if any(k in spec for k in ['reward_budget','reward_budgets','major_item_budget']):conflict('reward_budgets','typed_reward_budget_service_not_registered')
    calls=spec.get('budget',{}).get('generator_calls',1)
    if type(calls)is not int or calls<1:conflict('budget.generator_calls','positive_generation_budget_required')
    for pair in requested_pairs(spec):
        if pair!=['A','B']:verification.append(dict(field='relations',reason='ordered_pair_has_no_independent_evidence',missing_pair=pair))
    if conflicts or verification:
        return dict(status='needs_design'if conflicts else'needs_verification',conflicts=conflicts+verification,
            searched=dict(recipe=RECIPES[0],interfaces=[0,1],registered_pairs=[['A','B']],block_size=128),
            negotiable=['traversal role','Block128','jump+shot_recoil','no reward service','independent requested-direction verification'],
            may_delete_required_edges=False,new_physics_cases=0,production_admitted=False)
    c=rules.candidate(interface,control,0)
    extent=c['block_grid']['cells'];width=(max(p[0]for p in extent)-min(p[0]for p in extent)+1)*128;height=(max(p[1]for p in extent)-min(p[1]for p in extent)+1)*128
    space=spec.get('space',{})
    for key,actual in [('max_width',width),('max_height',height)]:
        if key in space and space[key]<actual:conflict('space.'+key,'current_actual_reserved_shape_exceeds_limit',actual=actual,requested=space[key])
    if conflicts:return dict(status='needs_design',conflicts=conflicts,searched=dict(interfaces=[interface]),new_physics_cases=0,production_admitted=False)
    response=dict(status='candidate_for_joint_mapping',request_id=spec['id'],source_request_sha256=digest(spec),
        satisfied_static_fields=['traversal role','Block128','connected reserved cells','boundary-center ground64 ports','required recoil/jump available','rewards=[]'],
        unresolved=['joint port-edge assignment','input/output state entailment','regional branch return composition','human difficulty intent'],
        registered_ordered_pairs=[['A','B']],explicit_reverse_supported=False,may_delete_required_edges=False,map_added_terrain=0,production_admitted=False)
    c['source_map_request']=copy.deepcopy(spec);c['map_request_response']=response
    c['map_specification']['objective']['source_map_request']=dict(id=spec['id'],sha256=digest(spec),preserve_all_edges=spec['objective'].get('preserve_all_edges',[]))
    c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
    return dict(status=response['status'],case=c,response=response)


def layouts(recipe,interface):
    if recipe!=RECIPES[0]:raise ValueError('unsupported_block_recipe')
    result=candidate_for_request(rules.real_request(),interface)
    if 'case'not in result:raise ValueError(result)
    return[result['case']]


def purpose(c,r):return rules.purpose(c,r)

def alternatives(c):return previous.alternatives(c)
