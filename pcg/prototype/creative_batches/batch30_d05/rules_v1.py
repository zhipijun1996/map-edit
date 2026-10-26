"""Human D05 variant: shoot a carrier-mounted bell, then be caught by that carrier."""
import copy,math
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.dynamic.generators import dynamic
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=('bell-carrier-catch',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/n for n in ['mount_v1.gd','runner_v1.gd','main_v1.gd','main_v1.tscn','protocol-v1.json']]
CAPS=['move','jump','shot_recoil']
def on_deck(after=0):return dynamic('wait','on_platform',after=after,timeout=180,query=dict(id='catch-deck'))
def candidate(interface=0,control=0):
 speed,shot=[(600,20),(750,20),(600,24),(750,24)][control]
 c=base(f'd05-bell-catch-i{interface}-c{control}');c['family']=RECIPES[0]
 c['platforms']=[[-160,438,400,100],[1220,330,300,120],[700,370,80,50],[-600,760,2300,60],[-560,680,120,30],[-420,600,120,30],[-280,520,120,30]]
 c['spawn']=[80,420];c['entry_port']=[80,420];c['exit_port']=[1320,312];c['goal']=[1295,308,50,8]
 c['moving_platforms']=[dict(platform_id='catch-deck',start=[360,450],finish=[950,450],size=[240,22],travel_duration=590/speed,dwell_duration=.2,initial_phase=0)]
 c['latches']=[dict(id='catch-bell',bell=[440,330],gate=[-400,-500,10,10],open_seconds=0,ferry_id='catch-deck',carrier_mount='catch-deck')]
 c['control_plan']=[cmd('axis',value=1),wait_x(355),on_deck(),cmd('axis',value=0),cmd('wait',8),cmd('axis',value=1),wait_x(425),cmd('jump'),cmd('jump_release',shot),cmd('shoot',0,aim_cell=dict(kind='bell',id='catch-bell')),on_deck(6),cmd('axis',value=0),cmd('wait',6),cmd('axis',value=1),wait_x(905),cmd('jump'),cmd('jump_release',16),cmd('shoot',6,direction=[-.8,.6]),settle(1320)]
 c['max_frames']=1500;c['trace_all']=False;c['interface']=interface;c['production_recipe']=RECIPES[0];c['reward_sites']=[];reward(c,1320,312,12);c['expected_reward']=12
 c['rule_parameters']=dict(interface=interface,control=control,speed=speed,first_shot_tick=shot,carrier_mount='catch-deck',first_departure_x=425,second_departure_x=905,roof=c['platforms'][2],purpose='same air shot starts moving support and creates interception landing, then actual grounded resource renewal supports second jump')
 c['generation_rule']=dict(id='human-d05/bell-carrier-catch',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters']);c['idea_ids']=['human-d05-bell-carrier-catch'];return c

def purpose(c,r):
 fs=r.get('frames',[]);reasons=[];shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle'];catch=[];initial=[];mounted=[]
 if not r.get('ok'):reasons.append(r.get('reason','unstable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):reasons.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):reasons.append('forbidden_ability')
 if r.get('returns'):reasons.append('unexpected_reset')
 if len(shots)<2:reasons.append('missing_two_phase_shots')
 if not toggles or not toggles[0]['running']or not toggles[0]['airborne']:reasons.append('same_air_shot_start_missing')
 if shots:
  initial=[f for f in fs if f['frame']<shots[0]['frame']and f.get('support_id')=='catch-deck'and f.get('grounded')]
  catch=[f for f in fs if shots[0]['frame']<f['frame']<(shots[1]['frame']if len(shots)>1 else 100000)and f.get('support_id')=='catch-deck'and f.get('grounded')]
  if shots[0]['requested']:
   dirs=[e.get('direction')for e in shots[0].get('accepted',[])if e.get('type')=='shot'];
   if not dirs or not(dirs[0][0]<0 and dirs[0][1]>0):reasons.append('first_shot_not_left_down')
 if not initial:reasons.append('never_stood_on_parked_deck')
 if not catch:reasons.append('not_caught_by_same_deck')
 refill=[f for f in catch if f.get('shot_charges',0)>=1]
 if not refill:reasons.append('no_real_ground_shot_refill')
 for f in fs:
  for m in f.get('workshop',{}).get('mounted_bells',[]):mounted.append(m)
 if not mounted or any(abs(m['receiver_offset'][0]-80)>.1 or abs(m['receiver_offset'][1]+120)>.1 for m in mounted):reasons.append('bell_not_really_mounted')
 if r.get('workshop',{}).get('coins',0)<c.get('expected_reward',0):reasons.append('reward_not_claimed')
 return dict(ok=not reasons,reasons=reasons,causal=dict(first_shot_frame=shots[0]['frame']if shots else None,carrier_toggles=toggles,initial_support_frames=len(initial),catch_frames=len(catch),actual_ground_refill_frames=len(refill),mounted_receiver_frames=len(mounted)),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps')))
