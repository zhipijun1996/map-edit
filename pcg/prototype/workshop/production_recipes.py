"""Bounded content recipes for the production loop; not online AI generation."""
import copy,math
from .rules import refund,base,cmd,wait_x,settle,reward,finish
from .evaluate import purpose as existing_purpose
from ..factory.core.quality import digest

RECIPES=('refund-turnback','bell-floor-drop')

def candidates(recipe,interface):
    if recipe=='refund-turnback':
        out=[]
        for delay in [20,22]:
            for dx in [.5,.7]:
                c=refund(interface);x=30-interface*40;y=100-interface*20
                c['id']=f'refund-turnback-{interface}-{delay}-{dx}'
                c['platforms'][1]=[x-90,y+18,180,80];c['platforms'][2]=[-500,680,1600,60]
                c['reward_sites']=[];reward(c,x,y,16)
                c['control_plan'][-2]=cmd('shoot',delay,direction=[dx,math.sqrt(1-dx*dx)])
                c['control_plan'][-1:]=[cmd('axis',value=-1,after=0),settle(x,6)]
                c.update(exit_port=[x,y],exit_normal=[-1,0],goal=[x-25,y-4,50,8],max_frames=600)
                c['production_recipe']=recipe;c['rule_parameters']=dict(relationship='air hit refund then reverse away from first recoil and land above the entry shore',interface=interface,delay=delay,second_aim_x=dx)
                c['generation_rule']=dict(id='workshop/production/'+recipe,version=1,parameters=c['rule_parameters'])
                out.append(c)
        return out
    if recipe=='bell-floor-drop':
        c=base('bell-floor-drop-'+str(interface));c['family']=recipe;c['production_recipe']=recipe
        x=380+interface*30
        c['platforms']=[[-160,438,460,300],[460+interface*60,438,340,300],[x-50,668,100,60],[-500,900,1600,60]]
        c['latches']=[dict(id='floor-bell',bell=[x,280],gate=[300,438,160+interface*60,20],open_seconds=1.0)]
        reward(c,x,650,10)
        c['rule_parameters']=dict(relationship='airborne upward bell shot recoils down through the removed floor',interface=interface)
        c=finish(c,x,650,[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),cmd('jump'),cmd('jump_release',8),cmd('shoot',aim_cell=dict(kind='bell',id='floor-bell')),settle(x,6)])
        c['production_recipe']=recipe
        return [c]
    raise ValueError('missing_generation_rule/'+recipe)

def purpose(c,r):
    if c['production_recipe']=='refund-turnback':
        p=existing_purpose(c,r);fs=r.get('frames',[]);shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))]
        # Count observed movement, not the requested direction word.
        reversal=any(a['vx']>80 and any(b['vx']< -80 for b in fs if a['frame']<b['frame']<=a['frame']+45)for a in fs if len(shots)>1 and shots[0]['frame']<=a['frame']<=shots[1]['frame'])
        p['causal']['observed_air_reversal']=reversal
        if not reversal:p['reasons'].append('air_turnback_not_executed')
        p['ok']=not p['reasons'];return p
    p=existing_purpose(c,r)
    events=r.get('plains',{}).get('events',[]);shots=[f for f in r.get('frames',[])if any(e['type']=='shot'for e in f.get('accepted',[]))]
    if not any(e['type']=='bell_open'for e in events)or not shots or shots[0]['grounded']:p['reasons'].append('air_shot_floor_relation_missing')
    p['ok']=not p['reasons'];return p

def specification(recipe,interface):
    c=candidates(recipe,interface)[0]
    return dict(schema='map-notes/challenge-specification/v1',id=f'production/{recipe}/{interface}',region='plains',required_family=c['family'],objective=dict(recipe=recipe,interface=interface),
        capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],c.get('exit_normal',[1,0])]),
        relations=[dict(from_port='entry',to_port='exit',role='reward')],entry_y=c['entry_port'][1],rise=c['entry_port'][1]-c['exit_port'][1],
        space=dict(max_width=1800,max_height=1200,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,risk_reward=dict(amount=c['reward_sites'][0]['amount'],mandatory_damage=False),
        difficulty=dict(intent='regular',human_score=None),resource_state=dict(reset_between_components=False,entry='original supported resources',exit='observed only'),return_conditions='UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))

def alternatives(c):
    from .counterexamples import alternatives as existing_alternatives
    out=existing_alternatives(c)
    if c['production_recipe']=='refund-turnback':
        for hold in [8,16,24]:
            for dx in [.5,.7,1.]:
                v=copy.deepcopy(c);v['id']+=f'-counter-direct-left-{hold}-{dx}';v['counterexample_kind']='direct-left'
                v['control_plan']=[cmd('axis',value=0),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[dx,math.sqrt(1-dx*dx)]),settle(c['exit_port'][0],6)];out.append(v)
    else:
        v=copy.deepcopy(c);v['id']+='-counter-ground-open-drop';v['counterexample_kind']='ground-open-drop'
        v['control_plan']=[cmd('axis',value=1),wait_x(c['exit_port'][0]),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='floor-bell')),settle(c['exit_port'][0],6)];out.append(v)
    return out
