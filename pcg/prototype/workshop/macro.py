"""Local executable Macro recipe on WorkshopEngine, not a Map generator.

Two independently versioned components own every solid and mechanism. Their
abutting shores introduce zero connector area. A full excursion is re-executed
with one actor, wallet and mechanism clock rather than concatenating traces.
"""
import argparse,copy,json
from .engine import ROOT,HERE,WorkshopEngine
from .rules import timed,base,cmd,wait_x,ground,settle,reward,finish
from .transitions import arrival
from .evaluate import instantiate
from .experiments import write
from ..factory.core.quality import digest,counts,gate,POLICY

FAMILY='gate-brake-return'

def recipe(variant):
    if variant not in (0,1):raise ValueError('unsupported_macro_interface')
    shift=40*variant;joint=600+shift;lip=730+shift
    pocket=[595+shift,632+20*variant];lower_y=900+20*variant
    a=timed(variant);a['family']=FAMILY+'-gate'
    # The right wall is deliberately removed in this NEW child version: the
    # reward has an authored descent, not a teleport or a reopened-door promise.
    front=a['platforms'][1][0]
    a['platforms']=[a['platforms'][0],[front,438,joint-front,100],a['platforms'][2],[-200,lower_y,joint-120+200,60],[270,650,110,45],[320,790,100,45]]
    a['latches'][0]['gate']=[front-20,240,20,198]
    a['latches'][0]['return_access']=[joint-50,350]
    a['reward_sites']=[];reward(a,joint-20,420,12)
    a['reward_sites'][0]['id']='gate-cache'
    a['ports']=[dict(id='A',position=[80,420],normal=[-1,0],support_index=0),dict(id='C',position=[joint-20,420],normal=[1,0],support_index=1),dict(id='R',position=[joint-140,lower_y-18],normal=[1,0],support_index=3)]
    a['entry_port']=[80,420];a['exit_port']=[joint-20,420]
    a['control_plan'][-1]=settle(joint-20,6)
    a['goal']=[joint-45,416,50,8]
    b=base('macro-brake-'+str(variant));b['family']=FAMILY+'-brake'
    b['platforms']=[[joint,438,lip-joint,100],[pocket[0]-50,pocket[1]+18,100,65],[joint-120,lower_y,1000-(joint-120),60]]
    b['ports']=[dict(id='D',position=[joint+20,420],normal=[-1,0],support_index=0),dict(id='B',position=pocket,normal=[-1,0],support_index=1),dict(id='E',position=[joint-100,lower_y-18],normal=[-1,0],support_index=2)]
    b['spawn']=b['entry_port']=[joint+20,420]
    b['exit_port']=pocket[:];b['goal']=[pocket[0]-25,pocket[1]-4,50,8]
    b['control_plan']=[cmd('axis',value=1),wait_x(lip+105),cmd('shoot',direction=[.9886859966642595,.15]),cmd('axis',value=-1),settle(pocket[0],6)]
    reward(b,*pocket,10)
    b['reward_sites'][0]['id']='brake-cache'
    for name,c in [('gate',a),('brake',b)]:
        c.update(max_frames=1000,rule_parameters=dict(recipe=FAMILY,version=1,variant=variant,component=name),generation_rule=dict(id='workshop/macro/'+FAMILY,version=1,component=name),idea_ids=['human-A3-short-gate','codex-brake-under-ledge-v1'])
        c['layout_uid']=digest(dict(recipe=FAMILY,variant=variant,component=name,platforms=c['platforms'],ports=c['ports'],latches=c['latches'],reward_sites=c['reward_sites']))
    return a,b

def scoped(c,rid,source,target,role,plan):
    c=copy.deepcopy(c);ports={p['id']:p for p in c['ports']}
    c.update(id=c['id']+'-'+rid,spawn=ports[source]['position'][:],entry_port=ports[source]['position'][:],exit_port=ports[target]['position'][:],control_plan=copy.deepcopy(plan))
    x,y=c['exit_port'];c['goal']=[x-25,y-4,50,8]
    c['route_spec']=dict(id=rid,from_port=source,to_port=target,role=role,via_ports=[],require_bell=rid=='gate')
    c['expected_reward']=12 if rid=='gate'else 10 if rid=='brake'else 0
    return c

def climb_plan():
    # Original settle is persistent, including after an axis command. Retarget
    # it explicitly at each observed landing instead of pretending axis cancels.
    return [settle(400),cmd('jump'),cmd('jump_release',20),ground(),cmd('wait',20),cmd('jump'),settle(335,14),cmd('jump_release',6),ground(),cmd('wait',20),cmd('jump'),cmd('jump_release',20),cmd('shoot',4,direction=[.5,.8660254037844386]),settle(80,9)]

def components(variant):
    a,b=recipe(variant);low=a['ports'][2]['position']
    out=[scoped(a,'gate','A','C','reward',a['control_plan']),scoped(a,'climb','R','A','return',climb_plan()),scoped(b,'brake','D','B','reward',b['control_plan']),scoped(b,'drop','B','E','return',[cmd('axis',value=-1),wait_x(low[0]+40,-1),settle(low[0]+40,6)])]
    out[-1]['expected_reward']=10
    return out

def macro_cases(variant):
    a,b=recipe(variant);parts=components(variant);g,climb,brake,drop=parts
    c=copy.deepcopy(a);c['id']='gate-brake-macro-'+str(variant);c['family']=FAMILY
    c['platforms']+=b['platforms'];c['reward_sites']+=b['reward_sites']
    c['ports']=[a['ports'][0],a['ports'][1],dict(b['ports'][1],support_index=len(a['platforms'])+1)]
    c['layout_uid']=digest(dict(recipe=FAMILY,variant=variant,components=[a['layout_uid'],b['layout_uid']]))
    c['rule_parameters']=dict(recipe=FAMILY,version=1,variant=variant,internal_seam_x=a['platforms'][1][0]+a['platforms'][1][2],lower_seam_x=a['platforms'][3][0]+a['platforms'][3][2],added_connector_area=0)
    # Junctions preserve the actual body, velocity, resources and clocks.
    gate_to_brake=arrival(g)+[cmd('axis',value=1),wait_x(b['entry_port'][0])]+b['control_plan']
    dock=b['ports'][2]['position'][0]
    return_to_a=[settle(dock),wait_x(dock+5,-1),ground(),cmd('wait',20),settle(a['ports'][2]['position'][0]),wait_x(a['ports'][2]['position'][0]+5,-1),ground(),cmd('wait',20)]+climb_plan()
    out=[scoped(c,'outbound','A','B','reward',gate_to_brake),scoped(c,'cache','A','C','reward',g['control_plan']),scoped(c,'descent','C','B','reward',[cmd('axis',value=1),wait_x(b['entry_port'][0])]+b['control_plan']),scoped(c,'return','B','A','return',return_to_a)]
    for case in out:
        case['expected_reward']={'outbound':22,'cache':12,'descent':22,'return':10}[case['route_spec']['id']]
        case['max_frames']=1400
    loop=copy.deepcopy(out[0]);loop['id']+='-continuous-loop';loop['route_spec']=dict(loop['route_spec'],id='loop',via_ports=['C','B','A'])
    # The legacy Module definition requires distinct active ports. This is an
    # additional same-world excursion specimen, not a fictional A->A port pair.
    loop['goal']=[55,416,50,8]
    loop['control_plan']=copy.deepcopy(out[0]['control_plan'])+[ground(),cmd('wait',20)]+return_to_a
    loop['expected_reward']=22;loop['max_frames']=1600
    return out,loop

def purpose(c,r):
    reasons=[];frames=r.get('frames',[]);rid=c['route_spec']['id'];part=c['family']
    if not r.get('ok'):reasons.append(r.get('reason','unstable'))
    if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
    if r.get('returns'):reasons.append('unexpected_return_or_teleport')
    if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):reasons.append('forbidden_ability')
    if r.get('workshop',{}).get('coins',0)!=c['expected_reward']:reasons.append('reward_transaction_mismatch')
    shots=[f for f in frames if any(e['type']=='shot'for e in f.get('accepted',[]))]
    causal={}
    if rid in ('gate','outbound','cache','loop'):
        bell=r.get('plains',{}).get('events',[])
        hits=[e for e in bell if e['type']=='bell_open']
        gx,gy,gw,gh=c['latches'][0]['gate']
        complete=next((f['frame']for f in frames if f['x']-12>=gx+gw),None)
        causal.update(gate_hit=hits[0]['frame']if hits else None,body_clear=complete)
        if not hits or not shots or shots[0]['grounded']or complete is None:reasons.append('airborne_same_shot_gate_missing')
    if rid in ('brake','outbound','descent','loop'):
        p=recipe(c['rule_parameters']['variant'])[1]['platforms'][0]
        brake_shots=[f for f in shots if f['x']>p[0]+p[2]and f['y']-18>p[1]+p[3]]
        causal['brake_below_lip_frames']=[f['frame']for f in brake_shots]
        if not brake_shots:reasons.append('brake_below_lip_missing')
    if rid=='loop':
        target=next(p['position']for p in c['ports']if p['id']=='B')
        visit=[f['frame']for f in frames if f['grounded']and abs(f['x']-target[0])<25 and abs(f['y']-target[1])<1]
        causal['visited_lower_cache_frames']=[min(visit),max(visit)]if visit else []
        if not visit:reasons.append('lower_port_not_visited')
    if rid in ('climb','return','loop'):
        visits=[]
        for x,y in [(400,772),(335,632)]:
            observed=any(f['grounded']and abs(f['x']-x)<25 and abs(f['y']-y)<1 for f in frames)
            visits.append(observed)
        causal['return_steps_actually_landed']=visits
        if not all(visits):reasons.append('return_step_missing')
    if rid in ('return','loop'):
        dock=recipe(c['rule_parameters']['variant'])[1]['ports'][2]['position']
        visited=any(f['grounded']and abs(f['x']-dock[0])<12 and abs(f['y']-dock[1])<1 for f in frames)
        causal['lower_internal_port_actually_landed']=visited
        if not visited:reasons.append('lower_internal_port_missing')
    return dict(ok=not reasons,reasons=reasons,causal=causal)

def run(name,stage='probe',include_components=True):
    engine=WorkshopEngine(ROOT/'results'/name);protocol=json.loads((HERE/'protocol-macro-port-v3.json').read_text());write(engine.out/'protocol.json',protocol)
    from .macro_interface import specifications,generate
    specs=specifications();write(engine.out/'challenge-specifications.json',specs)
    bases=[]
    for spec in specs:
        response=generate(spec)
        if response['status']!='requires_physics':raise ValueError(response)
        selected=(response['components']if include_components else [])+response['cases']+[response['continuous_fixture']]
        for c in selected:c['map_specification']=copy.deepcopy(spec)
        bases+=selected
    expanded=[];labels={}
    for b in bases:
        for level in (['clean']if stage=='probe'else ['clean','mild','moderate']):
            for i in range(1 if level=='clean'else 12):
                c=instantiate(b,protocol['holdout_seed']if stage=='holdout'else protocol['calibration_seed'],level,i)
                expanded.append(c);labels[c['id']]=(b['id'],level,i)
    write(engine.out/'cases.json',dict(cases=expanded));rows=[];reviews=[]
    for c,r,e in engine.run(expanded,stage):
        bid,level,i=labels[c['id']];p=purpose(c,r)
        row=dict(id=c['id'],base_id=bid,level=level,trial=i,purpose=p,safe_stable=bool(r['ok']),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),reason=r['reason'],last=[r['frames'][-1][k]for k in ['x','y']]if r.get('frames')else None,evidence=e)
        rows.append(row);write(engine.out/'rows.json',rows)
        if level=='clean':
            print(json.dumps(row),flush=True)
            if p['ok']:
                frozen=copy.deepcopy(c);frozen.update(factory_id=digest(next(b for b in bases if b['id']==bid)),factory_evidence=e,review_alias=bid,validation_summary='See evaluations.json')
                from ..factory.core.quality import module_hash
                frozen['recorded_frames']=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in r['frames']]
                frozen['module_sha256']=module_hash(frozen);reviews.append(frozen)
    entries=[]
    for b in bases:
        rs=[r for r in rows if r['base_id']==b['id']];stats={l:counts([r for r in rs if r['level']==l])for l in ['clean','mild','moderate']}
        entries.append(dict(id=b['id'],stats=stats,quality_gate=gate(stats,False,False)))
    write(engine.out/'evaluations.json',entries);write(engine.out/'review_cases.json',dict(cases=reviews));write(engine.out/'summary.json',dict(stage=stage,cases=len(rows),all_purpose_valid=all(r['purpose']['ok']for r in rows),passed_regular=all(e['quality_gate']['status']=='awaiting_human_review'for e in entries),entries=entries,human_playtest=False,production_admitted=False))
    print(engine.out,flush=True);return engine.out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['probe','calibration','holdout'],default='probe');p.add_argument('--macro-only',action='store_true');a=p.parse_args();run(a.name,a.stage,not a.macro_only)
