"""J03: two real elevation corridors and a shared open transfer courtyard.

Original fixed rock Cells and original character inputs only.  Each layout's
source scene is identical for every route; source port selects the initial body
location, never a different set of solids/rewards/resources.
"""
import copy, math
from pathlib import Path

HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json']
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd, wait_x, ground, settle
from pcg.prototype.factory.core.quality import digest

RECIPES=('woven-bridge-interchange',)
CAPS=['move','jump','shot_recoil']

def _port(id,xy,support,normal):
    return dict(id=id,position=xy,support_index=support,normal=normal)

def _upper(start,end,edge,sign):
    return [cmd('axis',value=sign),wait_x(edge,sign),cmd('jump'),cmd('jump_release',12),cmd('shoot',6,direction=[-sign*math.sqrt(1-.15**2),.15]),settle(end,6)]

def _lift(start,end,shaft):
    return [cmd('axis',value=1 if shaft>start else -1),wait_x(shaft,1 if shaft>start else -1),cmd('axis',value=0),cmd('wait',12),cmd('jump'),cmd('jump_release',20),cmd('shoot',0,direction=[-.35,math.sqrt(1-.35**2)]),cmd('axis',value=1),settle(end,10)]

def layouts(recipe,interface):
    if recipe not in RECIPES or interface not in (0,1):raise ValueError('unsupported exact bridge demand')
    # Interface 1 is narrower, taller and has an off-centre courtyard, rather
    # than the same photograph scaled/mirrored. All units are Godot world units.
    if interface==0:
        left,right,upper,lower,far,shaft=360,640,260,520,1040,540
    else:
        left,right,upper,lower,far,shaft=300,560,230,510,900,460
    c=base('junction-bridges');c['family']=RECIPES[0]
    c['platforms']=[[-120,upper,left+120,32],[right,upper,far-right+120,32],[-120,lower,far+240,80],[left+20,lower-110,90,22]]
    c['ports']=[_port('A',[60,upper-18],0,[-1,0]),_port('B',[far-60,upper-18],1,[1,0]),_port('C',[60,lower-18],2,[-1,0]),_port('D',[far-60,lower-18],2,[1,0])]
    c['world_bounds']=[-450,-450,far+900,1600]
    c['reward_sites']=[]
    ax,ay=c['ports'][0]['position'];bx,by=c['ports'][1]['position'];cx,cy=c['ports'][2]['position'];dx,dy=c['ports'][3]['position']
    down=[cmd('axis',value=1),wait_x(left+65),cmd('axis',value=0),ground(),cmd('wait',10),settle(dx)]
    lift=_lift(cx,bx,shaft)
    # Reaching D is observed without ending the run; no settle controller is
    # installed before the final destination. Axis braking uses the real motor.
    continuous_down=[cmd('axis',value=1),wait_x(left+65),cmd('axis',value=0),ground(),cmd('wait',10),cmd('axis',value=1),wait_x(dx-12),cmd('axis',value=0),cmd('wait',20),ground()]
    plans=[('upper-east','A','B','main',_upper(ax,bx,left-45,1),[],True),
           ('upper-to-lower','A','D','main',down,[],False),
           ('lower-east','C','D','main',[cmd('axis',value=1),settle(dx)],[],False),
           ('lower-to-upper','C','B','main',lift,[],True),
           ('upper-west','B','A','return',_upper(bx,ax,right+45,-1),[],True),
           ('lower-west','D','C','return',[cmd('axis',value=-1),settle(cx)],[],False),
           ('descend-then-lift','A','B','recovery',continuous_down+_lift(dx,bx,shaft),['D'],True)]
    physical={k:c.get(k,[])for k in ['platforms','ports','capabilities','one_way_platform_indices','wall_platform_indices','hazards','thorns','saws','moving_platforms','hooks','latches','enemies','reward_sites','world_bounds']}
    uid=digest(dict(recipe=recipe,interface=interface,physical=physical));out=[]
    for rid,frm,to,role,plan,via,recoil in plans:
        v=copy.deepcopy(c);start=next(p for p in c['ports']if p['id']==frm);end=next(p for p in c['ports']if p['id']==to)
        v.update(id=f'junction-bridges-{interface}-{rid}',layout_uid=uid,layout_title=f'交织双桥 / 四口 / {"宽中庭"if interface==0 else"偏心高庭"}',spawn=start['position'][:],entry_port=start['position'][:],exit_port=end['position'][:],goal=[end['position'][0]-25,end['position'][1]-4,50,8],control_plan=copy.deepcopy(plan),max_frames=1600,trace_all=False)
        v['route_spec']=dict(id=rid,from_port=frm,to_port=to,role=role,via_ports=via,require_bell=False)
        v['interface']=interface;v['production_recipe']=recipe;v['challenge_route']=False;v['expected_reward']=0;v['idea_ids']=['J03'];v['recoil_required_design']=recoil
        v['rule_parameters']=dict(interface=interface,upper_y=upper,lower_y=lower,courtyard=[left,right],shaft_x=shaft,port_roles=dict(A='west-upper-continuation',B='east-upper-continuation',C='west-lower-continuation',D='east-lower-continuation'),shared_choice='Upper approach chooses crossing or descent; lower courtyard chooses same-layer east corridor or ascent to upper east corridor',physical_layout_sha256=uid)
        v['generation_rule']=dict(id='junctions/J03',version=3,source_path=str(Path(__file__).relative_to(Path(__file__).resolve().parents[4])),parameters=v['rule_parameters'],source_type='current_codex_session_executable_rule')
        out.append(v)
    spec=dict(schema='map-notes/challenge-specification/v1',id=f'junctions/J03/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=recipe,objective=dict(recipe=recipe,junction_role='interchange',interface=interface,physical_layout_sha256=uid,ports=c['ports'],decision='same-level continuation versus actual elevation transfer'),capabilities=dict(version=1,status='defined',allOf=CAPS,anyOfGroups=[]),ports=dict(count=4,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port=v['route_spec']['from_port'],to_port=v['route_spec']['to_port'],route_id=v['route_spec']['id'],role=v['route_spec']['role'])for v in out],space=dict(max_width=1600,max_height=1100,max_port_span_x=1100),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=[]),resource_state=dict(reset_between_components=False,entry='original supported fresh scene at selected port; same unmodified starting character resources',exit='real observed stable state only; no universal transfer'),return_conditions='Only explicit continuous descend-then-lift demonstrates return from actual D visit; all untested pairs/states UNKNOWN',budget=dict(generator_candidates=1,director_revisions=0))
    for v in out:v['map_specification']=copy.deepcopy(spec)
    return out

def purpose(c,r):
    reasons=[];fs=r.get('frames',[]);causal={}
    if not r.get('ok'):reasons.append(r.get('reason','not_stable'))
    if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
    if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):reasons.append('forbidden_ability')
    if r.get('returns'):reasons.append('unexpected_reset')
    last=fs[-1]if fs else{}
    if not last.get('grounded')or abs(last.get('y',999999)-c['exit_port'][1])>1:reasons.append('destination_elevation_not_stably_reached')
    for pid in c['route_spec'].get('via_ports',[]):
        pos=next(p['position']for p in c['ports']if p['id']==pid)
        visited=any(f.get('grounded')and abs(f['x']-pos[0])<35 and abs(f['y']-pos[1])<1 for f in fs)
        causal['actual_visit_'+pid]=visited
        if not visited:reasons.append('missing_actual_via_port/'+pid)
    params=c['rule_parameters'];left,right=params['courtyard'];upper=params['upper_y'];lower=params['lower_y']
    courtyard=[f for f in fs if left-60<f['x']<right+40]
    causal.update(courtyard_frames=len(courtyard),height_range=[min((f['y']for f in fs),default=None),max((f['y']for f in fs),default=None)],body_size=[24,36],accepted_shots=r.get('shots',0),shot_necessity='unproven, tested separately')
    # Passage through the actual shared opening, not a prescribed shot sequence.
    if not courtyard:reasons.append('no_actual_shared_courtyard_visit')
    if c['route_spec']['id'] in ['lower-to-upper','descend-then-lift']:
        low=any(f.get('grounded')and abs(f['y']-(lower-18))<1 for f in fs)
        high=any(f.get('grounded')and abs(f['y']-(upper-18))<1 and f['x']>=right for f in fs)
        causal.update(actual_lower_ground=low,actual_upper_bank=high)
        if not low or not high:reasons.append('no_actual_elevation_transfer')
    return dict(ok=not reasons,reasons=reasons,causal=causal,behavior=dict(shots=r.get('shots',0),jumps=r.get('jumps',0)))

def alternatives(c):
    """18+ distinct controls. A valid alternative is allowed, not a rejection.

    Compare destination/actual via-port transactions separately before judging
    design purpose. The normal same-layer walk is an intended route.
    """
    out=[]
    def add(label,plan):
        v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
    for sign in [-1,1]:
        for delay in [0,12,30]:
            add(f'direct-walk-{sign}-{delay}',[cmd('axis',value=sign),cmd('wait',delay),settle(c['exit_port'][0],12)])
        for hold in [8,12,18,24,28]:
            add(f'ordinary-jump-{sign}-{hold}',[cmd('axis',value=sign),wait_x(c['rule_parameters']['shaft_x'],sign),cmd('jump'),cmd('jump_release',hold),settle(c['exit_port'][0],12)])
    for sign in [-1,1]:
        add(f'ground-premature-shot-{sign}',[cmd('shoot',direction=[sign,0]),cmd('axis',value=1 if c['exit_port'][0]>c['spawn'][0]else -1),settle(c['exit_port'][0],12)])
    if any(command['op']=='shoot'for command in c['control_plan']):
        for mode in ['omit-shots','reverse-shots']:
            plan=copy.deepcopy(c['control_plan'])
            for index,command in enumerate(plan):
                if command['op']!='shoot':continue
                if mode=='omit-shots':plan[index]=dict(op='wait',trigger=command['trigger'])
                else:command['direction']=[-x for x in command.get('direction',[0,1])]
            add(mode,plan)
    assert len({digest(v['control_plan'])for v in out})==len(out)
    return out
