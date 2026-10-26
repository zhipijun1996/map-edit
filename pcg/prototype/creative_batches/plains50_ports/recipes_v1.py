"""Five existing relationships adapted to explicit 3/4-port branch demands.

Only original Cells and programs; the original Godot engine certifies motion.
"""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.rules import thorn,timed,brake,fork,refund,cmd,wait_x,ground,settle
from pcg.prototype.workshop.evaluate import purpose as original_purpose
from pcg.prototype.workshop.counterexamples import alternatives as original_alternatives
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
RECIPES=('investment-fork','thorn-branch','brake-branch','timed-branch','refund-fork')

def port(name,xy,index,normal):return dict(id=name,position=xy,support_index=index,normal=normal)
def landing_plan(c):
    # Clear the persistent settle controller and genuinely visit a support.
    x,y=c['exit_port'];direction=1 if x>=c['spawn'][0]else -1
    return copy.deepcopy(c['control_plan'][:-1])+[wait_x(x-3*direction,direction),cmd('axis',value=0),ground(),cmd('wait',20)]

def layouts(recipe,interface):
    if recipe=='investment-fork':
        low,high=fork(0)
        c=copy.deepcopy(high);upper=[365+interface*20,232-interface*10];lower=[700+interface*30,532+interface*20]
        c['platforms'][1]=[upper[0]-65,upper[1]+18,130,24]
        c['platforms'][2]=[520,lower[1]+18,420+interface*20,100]
        c['ports']=[port('A',[80,420],0,[-1,0]),port('B',upper,1,[0,-1]),port('C',lower,2,[1,0])]
        c['reward_sites'][0].update(position=upper,region=[upper[0]-30,upper[1]-5,60,10])
        c['control_plan'][-1]=settle(upper[0],6)
        plans=[('reward','A','B','reward',c['control_plan'],True,[]),('main','A','C','main',copy.deepcopy(low['control_plan'][:-1])+[settle(lower[0],6)],False,[])]
        if not interface:
            c['exit_port']=upper
            plans.append(('reward-rejoin','A','C','recovery',landing_plan(c)+[cmd('axis',value=1),wait_x(upper[0]+105),settle(lower[0])],True,['B']))
        else:
            c['ports'].append(port('D',[1030,732],3,[1,0]))
            plans.append(('lower-exit','A','D','recovery',[cmd('axis',value=1),wait_x(235),cmd('axis',value=0),ground(),cmd('axis',value=1),settle(1030)],False,[]))
    elif recipe=='thorn-branch':
        c=thorn(0);front=475+interface*25;top=430-interface*10;target=[front+105,top-18]
        c['platforms'][1]=[front,top,220,160]
        c['reward_sites'][0].update(position=target,region=[target[0]-30,target[1]-5,60,10]);c['control_plan'][-1]=settle(target[0],6)
        lower=[-150 if not interface else 800,662]
        c['ports']=[port('A',[80,420],0,[-1,0]),port('B',target,1,[1,0]),port('C',lower,4,[-1,0]if not interface else[1,0])]
        safe=[cmd('axis',value=-1),wait_x(-185,-1),cmd('axis',value=0),ground(),settle(lower[0],4)]
        c['exit_port']=target
        tail=[cmd('axis',value=1),wait_x(front+265),cmd('axis',value=0),ground(),settle(lower[0],4)]
        plans=[('reward','A','B','reward',c['control_plan'],True,[]),('lower-exit','A','C','main',safe,False,[]),('reward-rejoin','A','C','recovery',landing_plan(c)+tail,True,['B'])]
    elif recipe=='brake-branch':
        c=brake(0);lip=252+interface*10;surface=456+interface*24;target=[110+interface*10,surface-18]
        c['platforms'][0]=[-160,180,lip+160,100];c['platforms'][1]=[target[0]-50,surface,100,65]
        c['reward_sites'][0].update(position=target,region=[target[0]-30,target[1]-5,60,10]);c['control_plan'][1]=wait_x(lip+105);c['control_plan'][-1]=settle(target[0],6)
        c['ports']=[port('A',[180,162],0,[-1,0]),port('B',target,1,[-1,0]),port('C',[900,662],2,[1,0])]
        c['exit_port']=target
        plans=[('reward','A','B','reward',c['control_plan'],True,[]),('lower-exit','A','C','main',[cmd('axis',value=1),settle(900)],False,[])]
        if not interface:plans.append(('reward-rejoin','A','C','recovery',landing_plan(c)+[cmd('axis',value=1),settle(900)],True,['B']))
        else:
            c['ports'].append(port('D',[-200,662],2,[-1,0]));plans.append(('west-exit','A','D','recovery',[cmd('axis',value=-1),wait_x(-205,-1),settle(-200)],False,[]))
    elif recipe=='timed-branch':
        c=timed(interface,window=.60 if not interface else .70)
        # New space demand moves the far receiver bank; the actual shot/door
        # opening relationship is re-measured rather than relabelled.
        c['platforms'][1][0]+=10;c['platforms'][1][2]+=10
        c['latches'][0]['gate'][0]+=10
        target=[c['exit_port'][0]+10,c['exit_port'][1]]
        c['reward_sites'][0].update(position=target,region=[target[0]-30,target[1]-5,60,10]);c['control_plan'][-1]=settle(target[0],6)
        c['ports']=[port('A',[80,420],0,[-1,0]),port('B',target,1,[1,0]),port('C',[-150,662],4,[-1,0])]
        safe=[cmd('axis',value=-1),wait_x(-185,-1),cmd('axis',value=0),ground(),settle(-150)]
        c['exit_port']=target
        tail=[cmd('axis',value=0),cmd('wait',90),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell',receiver='access')),cmd('axis',value=-1,after=8),wait_x(c['latches'][0]['gate'][0]-40,-1),settle(-150)]
        plans=[('reward','A','B','reward',c['control_plan'],True,[]),('lower-exit','A','C','main',safe,False,[])]
        if not interface:plans.append(('reward-rejoin','A','C','recovery',landing_plan(c)+tail,True,['B']))
        else:
            c['ports'].append(port('D',[970,662],4,[1,0]));plans.append(('east-lower-exit','A','D','recovery',safe[:-1]+[settle(970)],False,[]))
    elif recipe=='refund-fork':
        c=refund(0);target=[365+interface*20,100-interface*10]
        c['platforms'][1]=[target[0]-90,target[1]+18,210,80]
        c['reward_sites'][0].update(position=target,region=[target[0]-30,target[1]-5,60,10]);c['control_plan'][-1]=settle(target[0],6)
        c['ports']=[port('A',[80,420],0,[-1,0]),port('B',target,1,[1,0]),port('C',[1030,662],2,[1,0])]
        safe=[cmd('axis',value=1),wait_x(235),cmd('axis',value=0),ground(),settle(1030)]
        plans=[('reward','A','B','reward',c['control_plan'],True,[]),('lower-exit','A','C','main',safe,False,[])]
        if not interface:
            c['exit_port']=target
            plans.append(('reward-rejoin','A','C','recovery',landing_plan(c)+[cmd('axis',value=1),settle(1030)],True,['B']))
        else:
            left=[20,90];c['platforms'].append([-70,108,180,80]);c['ports'].append(port('D',left,3,[-1,0]))
            c['reward_sites'].append(dict(id='left-cache',position=left,region=[-10,85,60,10],amount=8))
            turn=copy.deepcopy(c['control_plan']);turn[-2]=cmd('shoot',22,direction=[.5,math.sqrt(.75)]);turn[-1:]=[cmd('axis',value=-1),settle(20,6)]
            plans.append(('turnback-reward','A','D','reward',turn,True,[]))
    else:raise ValueError('missing recipe/'+recipe)
    # All routes share every physical Cell, all reward transactions and initial
    # state. A marker without a qualified outgoing route is never enough.
    physical_keys=['capabilities','platforms','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','world_bounds','ports','reward_sites']
    layout=digest(dict(recipe=recipe,interface=interface,physical={k:c.get(k,[])for k in physical_keys}))
    out=[]
    for rid,from_port,to_port,role,plan,challenge,via in plans:
        v=copy.deepcopy(c);start=next(p for p in c['ports']if p['id']==from_port);end=next(p for p in c['ports']if p['id']==to_port)
        v.update(id=f'plains50-{recipe}-{interface}-{rid}',layout_uid=layout,layout_title=f'平原分叉 {recipe} / {len(c["ports"])}口 / {interface}',spawn=start['position'],entry_port=start['position'],exit_port=end['position'],goal=[end['position'][0]-25,end['position'][1]-4,50,8],control_plan=copy.deepcopy(plan),max_frames=1600,trace_all=False)
        v['route_spec']=dict(id=rid,from_port=from_port,to_port=to_port,role=role,via_ports=via,require_bell=challenge and recipe=='timed-branch')
        v['challenge_route']=challenge;v['production_recipe']=recipe;v['interface']=interface
        v['expected_reward']=8 if rid=='turnback-reward'else c['reward_sites'][0]['amount']if challenge else 0
        v['idea_ids']=['plains50-ports/'+recipe];v['rule_parameters']=dict(recipe=recipe,interface=interface,port_count=len(c['ports']),purpose='challenge exit plus intentionally allowed lower-risk branches',known_return='UNKNOWN except explicit continuously visited reward rejoin')
        v['generation_rule']=dict(id='plains50-ports/'+recipe,version=1,parameters=v['rule_parameters'])
        out.append(v)
    spec=dict(schema='map-notes/challenge-specification/v1',id=f'plains50/ports/{recipe}/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=c['family'],objective=dict(recipe=recipe,interface=interface,physical_layout_sha256=layout,branch_ports=c['ports']),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=len(c['ports']),required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port=v['route_spec']['from_port'],to_port=v['route_spec']['to_port'],role=v['route_spec']['role'],route_id=v['route_spec']['id'])for v in out],space=dict(max_width=2000,max_height=1400,max_port_span_x=1300),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='original fresh scene at selected supported port; captured before input',exit='observed stable only'),return_conditions='Only explicit reward-rejoin route retains actor/world; arbitrary returns UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
    for v in out:v['map_specification']=spec
    return out

def purpose(c,r):
    probe=copy.deepcopy(c)
    if not c['challenge_route']:
        probe['family']='safe-branch';probe['route_spec']['id']='recovery';probe['expected_reward']=0
    p=original_purpose(probe,r)
    for via in c['route_spec'].get('via_ports',[]):
        pos=next(x['position']for x in c['ports']if x['id']==via)
        visited=any(f['grounded']and abs(f['x']-pos[0])<30 and abs(f['y']-pos[1])<1 for f in r.get('frames',[]))
        p['causal']['visited_'+via]=visited
        if not visited:p['reasons'].append('missing_actual_via_port/'+via)
    if r.get('returns'):p['reasons'].append('unexpected_teleport_or_reset')
    p['ok']=not p['reasons'];return p

def alternatives(c):
    out=original_alternatives(c)
    # Both alternate exits and same-core variants are legitimate. Classification
    # always compares the exact source/destination, world and causal relation.
    for direction in [-1,1]:
        for delay in [0,8,20]:
            v=copy.deepcopy(c);v['id']+=f'-counter-direct-walk-{direction}-{delay}';v['counterexample_kind']='direct-walk'
            v['control_plan']=[cmd('axis',value=direction),cmd('wait',after=delay),settle(c['exit_port'][0])];out.append(v)
    return out
