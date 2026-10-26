"""Exact immutable-source content joins; no placement generator or new physics."""
import copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.transitions import arrival
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.factory.core.engine import file_sha
from pcg.map_directed.library import verified_document
from pcg.prototype.creative_batches.batch30_c01 import api_v1 as c01
from pcg.prototype.creative_batches.batch30_d05 import api_v3 as d05

HERE=Path(__file__).parent
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
C01=['9e704f9362715686ecdec8a56504f6fcce3020cdec88012e4eaa5d346659b111','baad7e601085c7d5804069daa69b3f1b94c9891141da08249517bcbec0cae3b2']
D05=['3b5ea33ef146c44fdf201ff3ebff5c4001fd398a0f532c1dbad068a7b17859b6','5ab81cab175d4b27d82c72ce6a0cfdcb51476584bfa9238b5cfcde14b80c6b43']
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json',HERE/'protocol-v2.json',HERE/'runner_v1.gd',HERE/'main_v1.gd',HERE/'main_v1.tscn',ROOT/'prototype/workshop/transitions.py',Path(c01.__file__),Path(d05.__file__)]+c01.SOURCE_DEPENDENCIES+d05.SOURCE_DEPENDENCIES


def source(version):
    folder=ROOT/'map_directed/library/candidates'/version
    doc=verified_document(folder/'module.mapnote.json')
    assert doc['generationContract']['contentVersion']=='sha256:'+version
    c=json.loads((folder/'cases.json').read_text())['cases'][0]
    binding=dict(contentVersion='sha256:'+version,case_id=c['id'],files={str((folder/n).relative_to(ROOT.parent)):file_sha(folder/n)for n in ['module.mapnote.json','record.json','cases.json']})
    return copy.deepcopy(c),binding


def rectangle(v,delta):return [v[0]+delta[0],v[1]+delta[1],*v[2:]]
def point(v,delta):return [v[0]+delta[0],v[1]+delta[1]]


def translated(c,delta):
    c=copy.deepcopy(c)
    assert not any(c.get(k)for k in ['enemies','saws','thorns','hooks','hazards']), 'This fixed adapter does not claim unsupported Cell transforms'
    for field in ['platforms']:
        c[field]=[rectangle(p,delta)for p in c[field]]
    for p in c.get('ports',[]):p['position']=point(p['position'],delta)
    for field in ['spawn','entry_port','exit_port']:c[field]=point(c[field],delta)
    for field in ['goal','world_bounds']:c[field]=rectangle(c[field],delta)
    for p in c['moving_platforms']:
        p['start']=point(p['start'],delta);p['finish']=point(p['finish'],delta)
    for latch in c['latches']:
        for field in ['gate','paired_gate']:
            if field in latch:latch[field]=rectangle(latch[field],delta)
        for field in ['bell','return_access']:
            if field in latch:latch[field]=point(latch[field],delta)
    for site in c['reward_sites']:
        site['position']=point(site['position'],delta);site['region']=rectangle(site['region'],delta)
    for q in c['control_plan']:
        if 'target_x'in q:q['target_x']+=delta[0]
        if 'aim_target'in q:q['aim_target']=point(q['aim_target'],delta)
        dynamic=q.get('trigger',{}).get('dynamic',{})
        if dynamic.get('kind')=='actor_x':dynamic['value']+=delta[0]
    return c


def intersection(a,b):
    x=max(a[0],b[0]);y=max(a[1],b[1]);w=min(a[0]+a[2],b[0]+b[2])-x;h=min(a[1]+a[3],b[1]+b[3])-y
    return [x,y,w,h]if w>0 and h>0 else None


def geometry_audit(left,right):
    allowed=[];conflicts=[]
    for i,a in enumerate(left['platforms']):
        for j,b in enumerate(right['platforms']):
            hit=intersection(a,b)
            if not hit:continue
            row=dict(left_static_index=i,right_static_index=j,overlap=hit)
            (allowed if a[1]==b[1]else conflicts).append(dict(row,classification='coplanar_original_shores'if a[1]==b[1]else 'foreign_static_solid_penetration'))
    for i,latch in enumerate(left['latches']):
        for field in ['gate','paired_gate']:
            if field not in latch:continue
            for j,solid in enumerate(right['platforms']):
                hit=intersection(latch[field],solid)
                if hit:conflicts.append(dict(left_mechanism=latch['id'],left_cell_part=field,right_static_index=j,overlap=hit,classification='foreign_solid_replaces_or_blocks_switchable_support'))
    for p in right['moving_platforms']:
        sx,sy=p['start'];ex,ey=p['finish'];w,h=p['size'];envelope=[min(sx,ex)-w/2,min(sy,ey)-h/2,abs(sx-ex)+w,abs(sy-ey)+h]
        for i,solid in enumerate(left['platforms']):
            hit=intersection(envelope,solid)
            if hit:conflicts.append(dict(left_static_index=i,right_carrier=p['platform_id'],envelope=envelope,overlap=hit,classification='foreign_solid_intersects_real_carrier_envelope'))
    return dict(allowed_original_coplanar_overlap=allowed,conflicts=conflicts,accepted=not conflicts)


def audited_pair(i,j):
    left,lb=source(C01[i]);right,rb=source(D05[j])
    delta=[left['exit_port'][k]-right['entry_port'][k]for k in range(2)]
    shifted=translated(right,delta)
    return left,shifted,dict(source_left=lb,source_right=rb,translation_right=delta,seam=left['exit_port'],audit=geometry_audit(left,shifted))


def candidate(i=0,j=0,control=0):
    left,right,meta=audited_pair(i,j)
    if not meta['audit']['accepted']:raise ValueError(meta['audit'])
    c=copy.deepcopy(left)
    for k in ['factory_id','factory_evidence','recorded_frames','module_sha256','validation_summary','review_alias','map_specification','noise']:c.pop(k,None)
    n=len(left['platforms'])
    c['platforms']=copy.deepcopy(left['platforms']+right['platforms'])
    for field in ['moving_platforms','latches']:c[field]=copy.deepcopy(left[field]+right[field])
    c['reward_sites']=[]
    for label,part in [('C01',left),('D05',right)]:
        for site in part['reward_sites']:c['reward_sites'].append(dict(copy.deepcopy(site),id=label+'/'+site['id']))
    for field in ['one_way_platform_indices','wall_platform_indices']:c[field]=left.get(field,[])+[n+k for k in right.get(field,[])]
    plan=arrival(left)
    if control==1:plan[-4]['trigger']['dynamic']['value']=left['exit_port'][0]-70
    c['control_plan']=plan+copy.deepcopy(right['control_plan'])
    x,y=right['exit_port'];c['spawn']=left['spawn'];c['entry_port']=left['entry_port'];c['exit_port']=right['exit_port'];c['goal']=[x-25,y-4,50,8]
    c['ports']=[dict(left['ports'][0],id='A'),dict(left['ports'][1],id='S'),dict(right['ports'][1],id='B',support_index=n+right['ports'][1]['support_index'])]
    c['route_spec']=dict(id='continuous-C01-D05',from_port='A',to_port='B',role='fixture',via_ports=['S'],required_rewards=['C01/visible-cache','D05/visible-cache'])
    c['required_rewards']=['C01/visible-cache','D05/visible-cache'];c['expected_reward']=24;c['max_frames']=2600;c['family']='paired-bridge-then-carrier-exact-seam';c['native_scene']=str(NATIVE_SCENE)
    c['id']=f'b30-seam-C01i{i}-D05i{j}-c{control}'
    c['seam_specimen']=dict(meta,source_left_case=left,source_right_case=right,added_solid_area=0,removed_solid_area=0,added_connector=False,union_geometry_sha256=digest(dict(static=c['platforms'],moving=c['moving_platforms'],doors=c['latches'])),continuous_state_no_reset=True,scope='Exact two existing Module versions under this translation and controller; not generic seam/transform admission')
    c['seam_specimen']['fixture_version']='sha256:'+digest(dict(sources=[meta['source_left']['contentVersion'],meta['source_right']['contentVersion']],translation=meta['translation_right'],geometry=c['seam_specimen']['union_geometry_sha256'],control_plan=c['control_plan']))
    assert c['platforms']==left['platforms']+right['platforms']
    assert c['moving_platforms']==left['moving_platforms']+right['moving_platforms']
    assert c['latches']==left['latches']+right['latches']
    a=left['world_bounds'];b=right['world_bounds'];minx=min(a[0],b[0]);miny=min(a[1],b[1]);c['world_bounds']=[minx,miny,max(a[0]+a[2],b[0]+b[2])-minx,max(a[1]+a[3],b[1]+b[3])-miny]
    return c


def purpose(c,raw):
    from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
    r,audit=classify(c,raw);fs=r.get('frames',[]);why=[];meta=c['seam_specimen'];join=meta['seam']
    source_check=c01.purpose(meta['source_left_case'],r)
    if not source_check['ok']:why+=['C01/'+x for x in source_check['reasons']]
    atjoin=[f for f in fs if f.get('grounded')and abs(f['x']-join[0])<=30 and abs(f['y']-join[1])<=1]
    start=atjoin[0]['frame']if atjoin else None
    partial=copy.deepcopy(r);partial['frames']=[f for f in fs if start is not None and f['frame']>=start]
    catch_check=d05.purpose(meta['source_right_case'],partial)
    if not catch_check['ok']:why+=['D05/'+x for x in catch_check['reasons']]
    if not atjoin:why.append('original_common_port_not_actually_visited_supported')
    claims=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='chest_claim'and e.get('accepted')]
    ids={e['id']for e in claims}
    if not set(c['required_rewards'])<=ids or r.get('workshop',{}).get('coins')!=24:why.append('both_original_chest_transactions_missing')
    if len([e for e in claims if e['id']in c['required_rewards']])!=2:why.append('reward_duplicate_or_missing')
    if not r.get('ok'):why.append(r.get('reason','not_stable'))
    if r.get('returns'):why.append('unexpected_reset_or_teleport')
    if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
    return dict(ok=not why,reasons=why,causal=dict(C01=source_check['causal'],D05=catch_check['causal'],supported_common_port_frames=[f['frame']for f in atjoin],claims=claims,added_solid_area=0,removed_solid_area=0,union_preserved=True,single_world=True,observer_interpretation=audit),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
