"""C03: carry an enemy-hit air refill across a real XOR window/path exchange."""
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
RECIPES=('refund-window-exchange',)
RUNNER_SCRIPT=CELL/'runner_v3.gd'
NATIVE_SCENE=CELL/'main_v3.tscn'
SOURCE_DEPENDENCIES=[HERE/'protocol-v1.json',*[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]]
def candidate(interface=0,control=0,route='air'):
 if interface!=0:raise ValueError('core first; second space not yet verified')
 c=base(f'b30-c03-v1-i{interface}-{route}-c{control}');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[-100,438,340,45],[350,100,240,60],[500,280,180,32],[-80,180,144,120],[-100,760,900,60],[-100,640,140,32],[100,540,220,32]]
 c['latches']=[dict(id='window-path-pair',bell=[155,395],gate=[40,300,24,138],paired_gate=[300,-200,24,480],initial_open='B')]
 c['enemies']=[dict(id='window-sentry',definition='plains_sentry',position=[0,422],initial_idle_cooldown=.6)]
 c['ports']=[dict(id='A',position=[80,420],normal=[-1,0],support_index=0),dict(id='B',position=[450,82],normal=[1,0],support_index=1)]
 c['spawn']=[80,420];c['entry_port']=[80,420];c['exit_port']=[450,82];c['goal']=[425,78,50,8]
 delay=[18,22,26,30][control]
 c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair')),cmd('wait',25),cmd('axis',value=0),cmd('jump'),cmd('axis',6,value=1),cmd('jump_release',10),cmd('shoot',6,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('shoot',delay,aim_cell=dict(kind='bell',id='window-path-pair')),settle(450,6)]
 c['max_frames']=1000;c['trace_all']=False;c['interface']=interface;c['production_recipe']=RECIPES[0];c['expected_reward']=12;c['reward_sites']=[];reward(c,450,82,12);c['required_rewards']=['visible-cache'];c['idea_ids']=['B30-C03'];c['native_scene']='res://prototype/creative_batches/batch30_c03/main_v1.tscn'
 c['route_spec']=dict(id=route,from_port='A',to_port='B',role='main',via_ports=[],require_bell=True,required_rewards=['visible-cache'])
 c['rule_parameters']=dict(interface=interface,control=control,route=route,first_hit_after_jump=22,bell_delay_after_hit_shot=delay,core='borrow original enemy air refund while window open then exchange it for passage openness with next recoil shot')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','enemies','latches','reward_sites']})
 c['layout_title']='借火以后把射窗封回去 / 侧龛高岸'
 c['generation_rule']=dict(id='batch30/C03',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('unexpected_reset')
 if r.get('workshop',{}).get('coins',0)<12:why.append('reward_missing')
 shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))]
 airshots=[f for f in shots if not f.get('grounded')]
 hits=[e for e in r.get('plains',{}).get('events',[])if e.get('type')=='enemy_hit']
 pair=r.get('workshop',{}).get('paired_gates',[]);switches=[e for p in pair for e in p.get('events',[])if e.get('type')=='pair_switch']
 if len(airshots)<2:why.append('two_actual_air_shots_missing')
 if not hits:why.append('actual_enemy_hit_missing')
 between=[f for f in fs if len(airshots)>=2 and airshots[0]['frame']<f['frame']<airshots[1]['frame']]
 if any(f.get('grounded')for f in between):why.append('air_refund_came_from_ground')
 refill=any(a.get('shot_charges')==0 and b.get('shot_charges')==1 and not a.get('grounded')and not b.get('grounded')for a,b in zip(between,between[1:]))
 if not refill:why.append('real_airborne_charge_refill_missing')
 if len(switches)<2 or switches[-1].get('open')!='B'or not switches[-1].get('airborne'):why.append('same_world_close_window_open_path_missing')
 return dict(ok=not why,reasons=why,causal=dict(air_shot_frames=[f['frame']for f in airshots],enemy_hits=hits,airborne_charge_refill=refill,pair_switches=switches),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps')))
