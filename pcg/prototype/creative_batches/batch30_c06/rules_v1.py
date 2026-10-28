"""C06: same-top-state falling fork with complementary exit commitment."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
RECIPES=('falling-gate-commitment',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/n for n in ['protocol-v1.json','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[HERE.parent/'batch30_c04/stable_support_names_v1.gd']+[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]
DELAYS=[18,22,26,30]

def materialize(interface=0,route='high',control=0):
 c=base('c06');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil'];old=[220,182]
 if interface==0:
  high=[-60,482];low=[510,782];sign=-1;launch=160
  c['platforms']=[[180,200,100,60],[-160,500,220,80],[400,800,220,100],[-250,1000,1000,40]]
  a=[90,-200,20,850];b=[360,-200,20,1200]
 else:
  high=[510,482];low=[510,932];sign=1;launch=300
  c['platforms']=[[180,200,100,60],[400,500,220,100],[400,950,220,100],[-200,1150,1000,40]]
  a=[360,-200,20,830];b=[360,630,20,520]
 c['spawn']=old;c['entry_port']=old;target=high if route=='high'else low;c['exit_port']=target;c['goal']=[target[0]-25,target[1]-4,50,8]
 c['latches']=[dict(id='branch-pair',bell=[230,540],gate=a,paired_gate=b,initial_open='B',open_seconds=0)]
 c['reward_sites']=[dict(id='high-cache',position=high,region=[high[0]-30,high[1]-6,60,12],amount=12),dict(id='low-cache',position=low,region=[low[0]-30,low[1]-6,60,12],amount=6)]
 if route=='high':
  c['control_plan']=[cmd('axis',value=sign),wait_x(launch,sign),cmd('axis',value=0),cmd('wait',DELAYS[control]),cmd('shoot',aim_cell=dict(kind='bell',id='branch-pair')),settle(target[0]),ground(),cmd('wait',10)]
 else:c['control_plan']=[cmd('axis',value=1),settle(target[0]),ground(),cmd('wait',10)]
 c['ports']=[dict(id='A',position=old,normal=[0,-1],support_index=0),dict(id='B',position=high,normal=[-1 if interface==0 else 1,0],support_index=1),dict(id='C',position=low,normal=[1,0],support_index=2)]
 c['route_spec']=dict(id='fall-to-'+route,from_port='A',to_port='B'if route=='high'else'C',role='main',via_ports=[],require_bell=route=='high')
 c['id']=f'b30-c06-v1-i{interface}-{route}-c{control}';c['interface']=interface;c['max_frames']=1500;c['trace_all']=False;c['production_recipe']=RECIPES[0];c['challenge_route']=True;c['expected_reward']=12 if route=='high'else 6;c['required_rewards']=['high-cache'if route=='high'else'low-cache'];c['idea_ids']=['B30-C06'];c['native_scene']='res://prototype/creative_batches/batch30_c06/main_v1.tscn'
 c['layout_title']='坠落中决定留在哪一层 / '+('左右错层石井'if interface==0 else'同侧高低双口')
 c['rule_parameters']=dict(interface=interface,route=route,control=control,fall_wait=DELAYS[control],direction=sign,launch_x=launch,core='same falling shot redirects body and opens high exit while closing low; failed high commitment changes real recovery world')
 c['generation_rule']=dict(id='batch30/C06',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','reward_sites']})
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id=f'batch30/C06/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],junction_role='falling_branch',core=c['rule_parameters']['core']),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=3,required_normals=[p['normal']for p in c['ports']]),relations=[dict(from_port='A',to_port='B',role='main',route_id='fall-to-high'),dict(from_port='A',to_port='C',role='main',route_id='fall-to-low')],space=dict(max_width=1400 if interface==0 else 1050,max_height=1500 if interface==0 else 1750,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='Same supported original A with Aclosed/Bopen, actual original single-air-shot resource',exit='Exact sampled chosen side and actual paired state; no interchangeable exits or arbitrary state transfer inferred'),return_conditions='Conditional same-world late-high miss and low recovery to be witnessed separately. All other ordered pairs UNKNOWN, no one-way proof.',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C06 exact spatial demands')
 return[materialize(interface,'high',0),materialize(interface,'low',0)]

def purpose(c,r):
 why=[];fs=r.get('frames',[]);state=(r.get('workshop',{}).get('paired_gates')or[{}])[0];events=[e for e in state.get('events',[])if e.get('type')=='pair_switch']
 claimed={e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 if not set(c['required_rewards'])<=claimed:why.append('required_reward_not_claimed')
 air_open=[e for e in events if e.get('open')=='A'and e.get('airborne')]
 falling=[]
 for shot in shots:
  before=next((f for f in fs if f['frame']==shot['frame']-1),None)
  if not shot.get('grounded')and before and before.get('vy',0)>100:falling.append(dict(frame=shot['frame'],x=shot['x'],y=shot['y'],before_vy=before['vy'],after_vy=shot['vy']))
 if c['rule_parameters']['route']=='high':
  if not any(e.get('open')=='A'for e in events):why.append('high_gate_never_opened')
  if r.get('shots',0)==1 and r.get('jumps',0)==0 and (not air_open or not falling):why.append('single_shot_falling_choice_missing')
  if r.get('shots',0)==0:why.append('high_choice_without_world_action')
 # Extra-jump or extra-shot planning may use a different valid order; it is
 # paid by real actions. Low exit is not forced to mimic the high programme.
 return dict(ok=not why,reasons=why,causal=dict(actual_pair_events=events,air_high_openings=air_open,falling_recoil_shots=falling,claimed_rewards=sorted(claimed),final_pair=state),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))

def alternatives(c):
 out=[];source=copy.deepcopy(c['control_plan']);route=c['rule_parameters']['route'];target=c['exit_port'][0];sign=c['rule_parameters']['direction'];launch=c['rule_parameters']['launch_x']
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 if route=='high':
  p=copy.deepcopy(source);p[4]=cmd('wait');add('omit-falling-shot',p)
  for delay in [6,12,18,24,30,36,44,52]:
   p=copy.deepcopy(source);p[3]['trigger']['after']=delay;add('fall-shot-window-'+str(delay),p)
  for x in [192,220,268]:
   move=1 if x>=220 else -1
   for hold in [0,20]:
    p=[cmd('axis',value=move),wait_x(x,move),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='branch-pair')),cmd('wait',20)]
    if hold:p += [cmd('axis',value=sign),cmd('jump'),cmd('jump_release',hold)]
    p += [settle(target),ground(),cmd('wait',10)];add(f'preopen-from-supported-top-{x}-{hold}',p)
  for dy in [.15,.7,.99]:
   p=copy.deepcopy(source);p[4].pop('aim_cell',None);p[4]['direction']=[-sign*math.sqrt(1-dy*dy),dy];add('fixed-recoil-miss-bell-'+str(dy),p)
 else:
  for hold in [0,8,16,24,28]:
   p=[cmd('axis',value=1)]
   if hold:p += [cmd('jump'),cmd('jump_release',hold)]
   p += [settle(target),ground(),cmd('wait',10)];add('low-route-ordinary-'+str(hold),p)
  for delay in [0,12,24,36,48,60,72,84]:
   p=[cmd('axis',value=1),cmd('shoot',delay,aim_cell=dict(kind='bell',id='branch-pair')),settle(target),ground(),cmd('wait',10)];add('low-while-swapping-world-'+str(delay),p)
  for dy in [.15,.7,.99]:
   for delay in [18,30]:
    p=[cmd('axis',value=1),cmd('shoot',delay,direction=[-math.sqrt(1-dy*dy),dy]),settle(target),ground(),cmd('wait',10)];add(f'low-paid-recoil-{dy}-{delay}',p)
 return out
