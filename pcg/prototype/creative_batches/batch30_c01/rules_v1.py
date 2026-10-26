"""C01: the same air shot removes the launch bridge and makes the landing bridge."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
RECIPES=('paired-support-transfer',)
RUNNER_SCRIPT=CELL/'runner_v3.gd'
NATIVE_SCENE=CELL/'main_v3.tscn'
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json',*[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]]
def at_ground_x(x,direction=1):
 return [wait_x(x,direction),cmd('axis',value=0),ground(),cmd('wait',8)]

def candidate(interface=0,control=0):
 if interface!=0:raise ValueError('Second space waits for actual core proof')
 c=base(f'b30-c01-v1-i{interface}-c{control}');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[-160,438,400,100],[1380,330,280,120],[-160,160,510,120],[-600,800,2300,60],[-500,680,160,35],[-340,560,160,35]]
 c['latches']=[dict(id='bridge-pair',bell=[440,390],gate=[220,438,340,24],paired_gate=[850,350,240,24],initial_open='B')]
 c['ports']=[dict(id='A',position=[80,420],normal=[-1,0],support_index=0),dict(id='B',position=[1490,312],normal=[1,0],support_index=1)]
 c['spawn']=[80,420];c['entry_port']=[80,420];c['exit_port']=[1490,312];c['goal']=[1465,308,50,8]
 delay=[14,18,22,26][control]
 c['control_plan']=[cmd('axis',value=1),wait_x(520),cmd('jump'),cmd('jump_release',delay),cmd('shoot',aim_cell=dict(kind='bell',id='bridge-pair')),cmd('wait',8),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),wait_x(1050),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[-.8,.6]),settle(1490,6)]
 c['max_frames']=1000;c['trace_all']=False;c['interface']=interface;c['production_recipe']=RECIPES[0];c['expected_reward']=12
 c['reward_sites']=[];reward(c,1490,312,12);c['required_rewards']=['visible-cache'];c['idea_ids']=['B30-C01'];c['native_scene']=str(NATIVE_SCENE)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites']})
 c['layout_title']='跳出去，桥才出现 / 断拱横渡'
 c['route_spec']=dict(id='support-swap',from_port='A',to_port='B',role='main',via_ports=[],require_bell=True,required_rewards=['visible-cache'])
 c['rule_parameters']=dict(interface=interface,control=control,shot_after_jump=delay,old_bridge=c['latches'][0]['gate'],new_bridge=c['latches'][0]['paired_gate'],core='same shot removes old support and creates new support; actual first landing and ground renewal')
 c['generation_rule']=dict(id='batch30/C01',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c

def over_bridge(f,rect):
 x,y,w,h=rect
 return bool(f.get('grounded'))and x-1<=f['x']<=x+w+1 and abs(f['y']+18-y)<1

def purpose(c,r):
 fs=r.get('frames',[]);why=[];shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('unexpected_reset')
 if r.get('workshop',{}).get('coins',0)<12:why.append('reward_not_claimed')
 first=shots[0]['frame']if shots else -1
 old=[f for f in fs if f['frame']<first and over_bridge(f,c['latches'][0]['gate'])and f['x']>360]
 landed=next((f for f in fs if f['frame']>first and f.get('grounded')),None)
 pair=r.get('workshop',{}).get('paired_gates',[])
 events=[e for p in pair for e in p.get('events',[])if e.get('type')=='pair_switch']
 swap=next((e for e in events if e.get('open')=='A'),None)
 if not old:why.append('old_bridge_actual_launch_position_missing')
 if not shots or shots[0].get('grounded')or not swap or not swap.get('airborne'):why.append('same_air_shot_support_swap_missing')
 if not landed or not over_bridge(landed,c['latches'][0]['paired_gate']):why.append('first_postshot_landing_not_new_bridge')
 if landed and landed.get('shot_charges',0)<1:why.append('new_bridge_ground_refill_missing')
 if len(shots)<2:why.append('second_phase_shot_missing')
 return dict(ok=not why,reasons=why,causal=dict(old_bridge_supported_frames=len(old),first_shot_frame=first,first_landing={k:landed.get(k)for k in ['frame','x','y','support_id','shot_charges']}if landed else None,pair_switches=events),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps')))
