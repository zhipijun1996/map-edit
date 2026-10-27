"""Same Block geometry with explicitly requested optional currency service."""
import copy,json
from pathlib import Path
from . import rules_v1 as geometry
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
REQUESTS=HERE.parents[2]/'creative-production/batch30/map-constraint-source-v1/generation/maps/map-requirements-review-v2/plan-0/challenge-specifications.json'
RECIPES=geometry.RECIPES
RUNNER_SCRIPT=geometry.RUNNER_SCRIPT
NATIVE_SCENE=geometry.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(geometry.__file__),*geometry.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json',REQUESTS]


def configured(c,reward_amount=0):
    if reward_amount not in [0,12]:raise ValueError('needs_design/only_none_or_original12currency_supported')
    c=copy.deepcopy(c)
    if reward_amount==0:c['reward_sites']=[]
    c['expected_reward']=reward_amount;c['required_rewards']=['visible-cache']if reward_amount else[]
    c['challenge_route']=bool(reward_amount)
    c['id']=c['id'].replace('block-c02-v1','block-c02-v2')+'-reward'+str(reward_amount)
    c['block_adaptation']['reward_request']=dict(currency=reward_amount,removed_original_chest=reward_amount==0,major_item_service='NOT_SUPPORTED')
    c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
    c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['block_adaptation'])
    c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
    c['map_specification']['risk_reward']['reward_sites']=copy.deepcopy(c['reward_sites'])
    return c


def candidate(interface=0,control=0,reward_amount=0):
    return configured(geometry.candidate(interface,control),reward_amount)


def real_request(request_id='block-demand/exp1_0'):
    return next(copy.deepcopy(s)for s in json.loads(REQUESTS.read_text())if s['id']==request_id)


def candidate_for_request(spec,interface=0,control=0):
    errors=[]
    if spec.get('schema')!='map-notes/challenge-specification/v1':errors.append('unsupported_challenge_schema')
    if spec.get('region')!='plains':errors.append('unsupported_region')
    if spec.get('block_grid',{}).get('size')!=128:errors.append('only_block128_physically_registered')
    if spec.get('ports',{}).get('count')!=2:errors.append('only_two_physical_ports_supported')
    if not set(spec.get('capabilities',{}).get('allOf',[]))<={'move','jump','shot_recoil'}:errors.append('unsupported_capability')
    if spec.get('rewards'):errors.append('typed_reward_request_requires_service_adapter; currency_not_a_major_item')
    if errors:return dict(status='needs_design',conflicts=errors,searched=dict(recipe=RECIPES[0],interfaces=[0,1],block_size=128),may_delete_required_edges=False,production_admitted=False)
    c=candidate(interface,control,0)
    response=dict(status='candidate_for_joint_mapping',request_id=spec['id'],source_request_sha256=digest(spec),
        satisfied_static_fields=['block_grid.size=128','two real boundary-center ports','connected reserved cells','only requested plains capabilities','rewards=[]'],
        unresolved=['joint port-edge assignment','exact requested ordered pairs','actual input/output state entailment','regional branch return composition','human difficulty intent'],
        local_direction=dict(from_port='A',to_port='B',status='staging prototype only; boundary fixture separate'),
        may_delete_required_edges=False,map_added_terrain=0,production_admitted=False)
    c['source_map_request']=copy.deepcopy(spec);c['map_request_response']=response
    c['map_specification']['objective']['source_map_request']=dict(id=spec['id'],sha256=digest(spec),preserve_all_edges=spec['objective']['preserve_all_edges'])
    return dict(status=response['status'],case=c,response=response)


def layouts(recipe,interface):
    if recipe!=RECIPES[0]:raise ValueError('unsupported_block_recipe')
    return[candidate_for_request(real_request(),interface)['case']]


def purpose(c,r):
    q=geometry.purpose(c,r)
    if c['expected_reward']==0:
        q['reasons']=[x for x in q['reasons']if x!='required_reward_not_claimed']
        if r.get('workshop',{}).get('coins',0)!=0:q['reasons'].append('none_reward_request_granted_currency')
    q['causal']['reward_requirement']=dict(required=c['expected_reward'],observed=r.get('workshop',{}).get('coins',0))
    q['ok']=not q['reasons'];return q


def alternatives(c):
    base=geometry.candidate(c['interface'],0)
    return[configured(v,c['expected_reward'])for v in geometry.alternatives(base)]
