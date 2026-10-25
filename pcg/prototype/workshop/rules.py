"""Executable terrain/Cell rules. Inputs select registered relationships only.

No physics estimates certify playability: measured construction is followed by
the original Motor, Router, damage, projectile and resource components.
"""
import copy, math
from .measure import base
from ..plains.synthesis import command as cmd
from ..factory.core.quality import digest

FAMILIES=('thorn-slot','chase-landing','timed-cache','brake-under-ledge','one-shot-two-routes','air-refund')
def wait_x(x, direction=1):
    return dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte'if direction>0 else'lte',value=x),timeout=180))
def ground():return dict(op='wait',trigger=dict(state='grounded',timeout=240))
def settle(x,after=0):return cmd('settle',after,target_x=x,deadband=4)
def reward(c,x,y,amount=8):
    c['reward_sites'].append(dict(id='visible-cache',position=[x,y],region=[x-30,y-5,60,10],amount=amount))
def finish(c,x,y,plan):
    c.update(exit_port=[x,y],goal=[x-25,y-4,50,8],control_plan=plan,max_frames=720,trace_all=False)
    c['generation_rule']=dict(id='workshop/'+c['family'],version=1,parameters=c.get('rule_parameters',{}),
        source_type='executable_rule',human_fun='unreviewed')
    return c
def launch(hold=8,shot=16,dy=.15,takeoff=205):
    return [cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',hold),cmd('shoot',shot-hold,direction=[-math.sqrt(1-dy*dy),dy])]

def thorn(variant):
    c=base('thorn-slot-'+str(variant));c['family']='thorn-slot'
    left=460+variant*30;surface=438-variant*20
    c['platforms'] += [[left,surface,220,160],[260,80,240+variant*30,200],[280,444,150+variant*20,90],[-200,680,1100,60]]
    c['thorns']=[dict(surface_id='upper-slot',platform_index=2,face='bottom',start_offset=0,length=240+variant*30,depth=12),dict(surface_id='lower-slot',platform_index=3,face='top',start_offset=0,length=150+variant*20,depth=12)]
    x=left+105;y=surface-18
    c['rule_parameters']=dict(landing_front=left,landing_y=surface,slot_body=[24,36],open_band=[292,432])
    reward(c,x,y)
    return finish(c,x,y,launch()+[settle(x,6)])

def timed(variant,window=.55):
    c=base('timed-cache-'+str(variant));c['family']='timed-cache'
    left=460+variant*20;right=730+variant*40;surface=438-variant*10
    c['platforms'] += [[left,surface,right-left,100],[250,80,right-250+30,160],[right,240,30,surface-240],[-200,680,1200,60]]
    c['latches']=[dict(id='short-bell',bell=[190,405],gate=[left-20,240,20,surface-240],open_seconds=window,return_access=[right-60,350])]
    x=right-65;y=surface-18
    plan=launch();plan[4]=cmd('shoot',8,aim_cell=dict(kind='bell',id='short-bell'))
    c['rule_parameters']=dict(gate_window_seconds=window,door_x=left-20,body_size=[24,36],timer_policy='solve from actual hit and complete-body crossing; safe close retained')
    reward(c,x,y,12)
    return finish(c,x,y,plan+[settle(x,6)])

def chase(variant):
    c=base('chase-landing-'+str(variant));c['family']='chase-landing'
    dx=variant*35
    c['platforms'] += [[590+dx,288,220,100],[-200,650,1300,60]]
    c['moving_platforms']=[dict(platform_id='chase-carrier',start=[340,450],finish=[560+dx,350],size=[144,22],travel_duration=1.4+variant*.2,dwell_duration=.15,initial_phase=0)]
    c['latches']=[dict(id='carrier-bell',bell=[105,430],gate=[-500,-500,10,10],open_seconds=0,ferry_id='chase-carrier',return_access=[370,370])]
    x=680+dx;y=270
    plan=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',8),cmd('shoot',10,aim_cell=dict(kind='bell',id='carrier-bell')),cmd('wait',6),
          dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='chase-carrier'),timeout=180)),cmd('axis',value=0),cmd('wait',18),
          cmd('axis',value=1),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,aim_cell=dict(kind='bell',id='carrier-bell',receiver='access')),settle(x,6)]
    c['rule_parameters']=dict(carrier_travel=[220+dx,-100],controls='original start/pause only; no new carrier behavior',passive_wait_must_not_finish=True)
    reward(c,x,y)
    return finish(c,x,y,plan)

def brake(variant):
    c=base('brake-under-ledge-'+str(variant));c['family']='brake-under-ledge'
    surface=438+variant*30;lip=240+variant*20
    c['platforms']=[[-160,180,lip+160,100],[45,surface,100,65],[-240,680,1240,60]]
    c['spawn']=[180,162];c['entry_port']=[180,162]
    x=105;y=surface-18
    # Falling commits to the outside of the rock lip; shoot right to brake and
    # redirect into its underside pocket. The same rectangle supports the entry.
    plan=[cmd('axis',value=1),wait_x(lip+105),cmd('shoot',direction=[1,0]),cmd('axis',value=-1,after=9),settle(x,6)]
    c['rule_parameters']=dict(lip_x=lip,pocket_y=surface,shot_role='brake and turn left after falling below lip')
    reward(c,x,y,10)
    return finish(c,x,y,plan)

def fork(variant):
    c=base('one-shot-two-routes-'+str(variant));c['family']='one-shot-two-routes'
    upper=[355+variant*25,232-variant*20];low=[650+variant*30,532]
    c['platforms'] += [[upper[0]-65,upper[1]+18,130,24],[520,550,360+variant*30,100],[-200,750,1300,60]]
    c['ports']=[dict(id='A',position=[80,420],normal=[-1,0],support_index=0),dict(id='B',position=low,normal=[1,0],support_index=2),dict(id='C',position=upper,normal=[0,-1],support_index=1)]
    c['rule_parameters']=dict(resource='one original air shot, renewed only by actual ground contact or enemy hit',upper=upper,lower=low)
    reward(c,*upper,12)
    c['layout_uid']=digest({k:c[k]for k in ['family','platforms','ports','reward_sites']})
    high=launch(12,18,.866,takeoff=140)+[settle(upper[0],6)]
    lowplan=launch(8,16,.15)+[settle(low[0],6)]
    # Initial routes share every physical Cell; untested ordered pairs stay UNKNOWN.
    out=[]
    for rid,target,role,plan in [('low','B','main',lowplan),('high','C','reward',high)]:
        v=copy.deepcopy(c);p=next(p for p in c['ports']if p['id']==target)
        v['id']+='-'+rid;v['route_spec']=dict(id=rid,from_port='A',to_port=target,role=role,via_ports=[],require_bell=False)
        out.append(finish(v,*p['position'],plan))
    return out

def refund(variant):
    c=base('air-refund-'+str(variant));c['family']='air-refund'
    x=350+variant*30;y=100-variant*20
    c['platforms'] += [[x-90,y+18,210,80],[-200,680,1300,60]]
    c['enemies']=[dict(id='ammo-sentry',definition='plains_sentry',position=[125,422],initial_idle_cooldown=.6)]
    plan=[cmd('axis',value=0),cmd('jump'),cmd('axis',6,value=1),cmd('jump_release',10),cmd('shoot',6,aim_cell=dict(kind='enemy',id='ammo-sentry')),cmd('shoot',18,direction=[-.5,.8660254037844386]),settle(x,6)]
    c['rule_parameters']=dict(landing=[x,y],enemy_role='actual airborne hit resource opportunity and attack threat')
    reward(c,x,y,16)
    return finish(c,x,y,plan)

REGISTRY=dict(zip(FAMILIES,[thorn,chase,timed,brake,fork,refund]))

def candidates(family,variant):
    result=REGISTRY[family](variant)
    return result if isinstance(result,list)else[result]

def specifications():
    out=[]
    for family in FAMILIES:
        for variant in range(2):
            c=candidates(family,variant)[0]
            out.append(dict(schema='map-notes/challenge-specification/v1',id=f'workshop/{family}/{variant}',region='plains',
                required_family=family,objective=c['rule_parameters'],capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),
                ports=dict(count=len(c.get('ports',[]))or 2,required_normals=[p['normal']for p in c['ports']]if c.get('ports')else[[-1,0],[1,0]]),
                relations=[dict(from_port='A',to_port='B',role='main'),dict(from_port='A',to_port='C',role='reward')]if c.get('ports')else[dict(from_port='entry',to_port='exit',role='reward')],
                entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],
                space=dict(max_width=1800,max_height=1000,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,
                risk_reward=dict(amount=c['reward_sites'][0]['amount'],mandatory_damage=False),difficulty=dict(intent='regular',human_score=None),
                resource_state=dict(reset_between_components=False,entry='supported, original fresh resources, exact capture before input',exit='stable original ground state; universal transfer UNKNOWN'),
                return_conditions='UNKNOWN until continuous witness exists',budget=dict(generator_candidates=12,director_revisions=0)))
    return out

def generate(spec):
    """Exact bounded domains initially. Never accept caller implemented=true."""
    family=spec.get('required_family')
    if family not in REGISTRY:return dict(status='unsatisfied',conflicts=[dict(field='required_family',reason='missing_generation_rule',value=family)],searched=dict(families=list(FAMILIES)),negotiable=['registered relationship or new isolated rule implementation'])
    supported=[s for s in specifications()if s['required_family']==family]
    keys=['region','capabilities','ports','space','entry_y','rise','risk_reward','boundary_policy','enclosing_walls','objective','relations','resource_state','return_conditions','difficulty']
    for index,s in enumerate(supported):
        if all(spec.get(k)==s.get(k)for k in keys):return dict(status='requires_physics',cases=candidates(family,index),matched_specification=s['id'],production_admitted=False)
    return dict(status='unsatisfied',conflicts=[dict(field=k,reason='outside_registered_generation_domain',requested=spec.get(k),supported=[s.get(k)for s in supported])for k in keys if not any(spec.get(k)==s.get(k)for s in supported)],searched=dict(interfaces=[s['id']for s in supported],geometry_candidates=len(supported),unbounded_search=False),negotiable=['one of the explicit supported interfaces; no automatic substitutions'])
