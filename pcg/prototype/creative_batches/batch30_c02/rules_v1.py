"""C02: original-air-shot state order through two complementary doors."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
RECIPES=('serial-airlock-recoil',)
RUNNER_SCRIPT=CELL/'runner_v3.gd'
NATIVE_SCENE=CELL/'main_v3.tscn'
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json']+[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]

def materialize(interface=0,control=0):
 c=base('c02');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 # Local gate pillars join the roof and safe recovery floor; no outside frame.
 c['platforms']=[[-160,438,400,100],[680,438,280,100],[250,80,370,50],[-500,900,1160,40],[-480,790,100,28],[-390,670,100,28],[-300,550,100,28],[-210,438,100,28]]
 c['spawn']=[80,420];c['entry_port']=[80,420];c['exit_port']=[820,420]
 c['latches']=[dict(id='airlock-pair',bell=[220,405],gate=[270,130,20,770],paired_gate=[550,130,20,770],initial_open='A',open_seconds=0,return_access=[430,800])]
 c['reward_sites']=[];reward(c,820,420,12)
 shot=[10,14,18,22][control]
 c['control_plan']=[cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',12),cmd('shoot',shot,aim_cell=dict(kind='bell',id='airlock-pair')),settle(820,6)]
 c['goal']=[795,416,50,8];c['max_frames']=1200;c['trace_all']=False
 c['ports']=[dict(id='A',position=[80,420],normal=[-1,0],support_index=0),dict(id='B',position=[820,420],normal=[1,0],support_index=1)]
 c['route_spec']=dict(id='cross-A-swap-cross-B',from_port='A',to_port='B',role='main',via_ports=[],require_bell=True)
 c['id']=f'b30-c02-v1-i{interface}-c{control}';c['interface']=interface;c['production_recipe']=RECIPES[0];c['challenge_route']=True;c['expected_reward']=12;c['required_rewards']=['visible-cache']
 c['idea_ids']=['B30-C02'];c['native_scene']=str(NATIVE_SCENE)
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','moving_platforms','latches','reward_sites']})
 c['layout_title']='先穿第一门，再换第二门 / 横向断拱'
 c['rule_parameters']=dict(interface=interface,control=control,hold=12,shot_after_release=shot,core='full body clears A before original air shot closes it and opens B; same recoil crosses unsupported middle')
 c['generation_rule']=dict(id='batch30/C02',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['map_specification']=dict(schema='map-notes/challenge-specification/v1',id=f'batch30/C02/{interface}',source_type='model_authored_challenge_spec',region='plains',required_family=RECIPES[0],objective=dict(recipe=RECIPES[0],interface=interface,physical_layout_sha256=c['layout_uid'],core=c['rule_parameters']['core']),capabilities=dict(version=1,status='defined',allOf=c['capabilities'],anyOfGroups=[]),ports=dict(count=2,required_normals=[[-1,0],[1,0]]),relations=[dict(from_port='A',to_port='B',role='main',route_id=c['route_spec']['id'])],space=dict(max_width=1500,max_height=900,max_port_span_x=900),boundary_policy='open',enclosing_walls=False,difficulty=dict(intent='regular',human_score=None),risk_reward=dict(mandatory_damage=False,reward_sites=c['reward_sites']),resource_state=dict(reset_between_components=False,entry='original fresh supported A, pair A open/B closed',exit='observed stable B with A closed/B open; arbitrary states UNKNOWN'),return_conditions='lower recovery nominal design; exact continuous recovery tested separately, B to A UNKNOWN',budget=dict(generator_candidates=4,director_revisions=0))
 return c

def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('unsupported exact C02 demand')
 return [materialize(interface,0)]

def purpose(c,r):
 fs=r.get('frames',[]);why=[];pairs=r.get('workshop',{}).get('paired_gates',[]);state=pairs[0]if pairs else{};events=state.get('events',[])
 swaps=[e for e in events if e.get('type')=='pair_switch']
 first=next((e for e in swaps if e.get('open')=='B'),None)
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 if r.get('workshop',{}).get('coins',0)<12:why.append('required_reward_not_claimed')
 if not first or not first.get('airborne'):why.append('airborne_pair_swap_missing')
 near=c['latches'][0]['gate'];far=c['latches'][0]['paired_gate']
 before=next((f for f in fs if first and f['frame']==first['frame']),None)
 if not before or before['x']-12<near[0]+near[2]+6:why.append('body_not_clear_of_closing_A')
 crossing=[f for f in fs if f['x']-12>=near[0]+near[2]and f['x']+12<=far[0]]
 if not crossing or any(f.get('grounded')for f in crossing):why.append('unsupported_middle_not_preserved')
 after=[f for f in fs if first and f['frame']>=first['frame']and f['x']-12>=far[0]+far[2]]
 if not after:why.append('body_never_crossed_open_B')
 if state.get('open_a')is not False or state.get('open_b')is not True:why.append('wrong_final_gate_state')
 return dict(ok=not why,reasons=why,causal=dict(actual_swap=first,swap_body=({k:before.get(k)for k in ['frame','x','y','grounded','shot_charges']}if before else None),unsupported_middle_frames=len(crossing),gate_B_crossing_frames=len(after),pair_final=state),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))

def alternatives(c):
 out=[]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 plan=copy.deepcopy(c['control_plan']);plan[4]=cmd('wait',plan[4]['trigger']['after']);add('omit-air-shot',plan)
 for hold in [6,12,20,28]:
  add(f'ordinary-hold-{hold}',[cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',hold),settle(820,6)])
  for dy in [.15,.6,.95]:
   add(f'fixed-recoil-no-switch-{hold}-{dy}',[cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(820,6)])
 for delay in [0,12,24,48]:
  add(f'early-ground-swap-{delay}',[cmd('shoot',aim_cell=dict(kind='bell',id='airlock-pair')),cmd('wait',delay)]+copy.deepcopy(c['control_plan']))
 for delay in [6,12,18,24]:
  p=copy.deepcopy(c['control_plan']);p[4]['trigger']['after']=delay;add(f'changed-air-window-{delay}',p)
 return out
