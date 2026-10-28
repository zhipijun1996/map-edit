"""Continuous upper stonecrown excursion, lower belly return, original state."""
from pathlib import Path
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle,reward
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
CELL=HERE.parent/'batch30_cell'
RECIPES=('persistent-upper-lower-return',)
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[HERE/n for n in ['proposal-source-v1.json','protocol-v1.json','runner_v1.gd','main_v1.gd','main_v1.tscn']]+[CELL/n for n in ['pair_latch_v1.gd','pair_latch_v2.gd','pair_latch_v3.gd','runtime_v3.gd','runner_v3.gd','main_v3.gd','main_v3.tscn']]
def rest():return[ground(),cmd('wait',8)]
def outbound(hold):
 return[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,aim_cell=dict(kind='bell',id='return-pair')),settle(400,6),wait_x(396),*rest(),settle(470),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=[0,1]),settle(470,6),*rest(),settle(560),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=[0,1]),settle(560,6),*rest(),settle(900),wait_x(896),*rest(),cmd('wait',12)]
def returning(delay=32):
 return[settle(800),wait_x(804,-1),cmd('wait',delay),cmd('shoot',aim_cell=dict(kind='bell',id='return-pair',receiver='access')),settle(600,6),wait_x(604,-1),*rest(),settle(280),wait_x(284,-1),cmd('jump'),cmd('jump_release',32),settle(80,6)]
def candidate(interface=0,control=0,route='loop'):
 if interface!=0:raise ValueError('Secondspace waits for actual wholeloop core')
 c=base(f'b30-c09-v1-i0-{route}-c{control}');c['family']=RECIPES[0];c['capabilities']=['move','jump','shot_recoil']
 c['platforms']=[[0,1000,240,80],[330,740,160,60],[450,460,100,100],[500,200,210,620],[820,600,200,550],[260,1100,450,40],[-160,1320,1400,60],[-160,1170,180,30],[1060,1170,140,30]]
 c['latches']=[dict(id='return-pair',bell=[190,970],gate=[750,-200,24,800],paired_gate=[750,820,24,280],initial_open='B',return_access=[810,880])]
 c['ports']=[dict(id='A',position=[80,982],normal=[-1,0],support_index=0),dict(id='B',position=[900,582],normal=[1,0],support_index=4)]
 c.update(spawn=[80,982],entry_port=[80,982],exit_port=[900,582],goal=[55,978,50,8],interface=0,trace_all=False,max_frames=2400,production_recipe=RECIPES[0],idea_ids=['B30-C09'],native_scene='res://prototype/creative_batches/batch30_c09/main_v1.tscn',expected_reward=16)
 hold=[12,16,20,24][control];plan=outbound(hold)
 if route=='loop':plan+=returning()
 elif route=='outbound':c['goal']=[875,578,50,8]
 else:raise ValueError('Unregistered C09 route')
 c['control_plan']=plan;c['reward_sites']=[];reward(c,900,582,16);c['required_rewards']=['visible-cache']
 c['route_spec']=dict(id=route,from_port='A',to_port='B',role='main',via_ports=['B','A']if route=='loop'else[],require_bell=True,required_rewards=c['required_rewards'])
 c['required_pair_states']=[dict(id='return-pair',open_a=route=='outbound',open_b=route=='loop')]
 c['rule_parameters']=dict(interface=0,control=control,first_jump_release=hold,firstshot6later=True,return_wait_at_shaft=32,core='three original recoil climbs onto stonecrown,400-unitdrop to farreward, original returnreceiver simultaneously shuts high/openlow, lowerbelly return instead highroute reversed')
 c['layout_title']='去程走高，回程把空间翻到低处 / 石冠腹下'
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites']})
 c['generation_rule']=dict(id='batch30/C09',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 fs=r.get('frames',[]);why=[]
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage'):why.append('player_harm')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('returns'):why.append('world_reset')
 claimed=[e for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')]
 if len(claimed)!=1 or r.get('workshop',{}).get('coins')!=16:why.append('one_real_reward_transaction_missing')
 pair=next((p for p in r.get('workshop',{}).get('paired_gates',[])if p['id']=='return-pair'),{})
 switches=[e for e in pair.get('events',[])if e.get('type')=='pair_switch']
 b=[f for f in fs if f.get('grounded')and abs(f['x']-900)<30 and abs(f['y']-582)<1]
 if not b:why.append('actual_far_reward_port_missing')
 upper=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform3']
 if not upper:why.append('actual_stonecrown_support_missing')
 if c['route_spec']['id']=='loop':
  lower=[f for f in fs if b and f['frame']>b[0]['frame']and f.get('grounded')and f.get('support_id')=='Platform5']
  if not lower:why.append('actual_distinct_lower_return_support_missing')
  if len(switches)!=2 or switches[0].get('open')!='A'or switches[-1].get('open')!='B':why.append('same_world_high_low_flip_missing')
  if len(switches)>=2 and b and switches[-1]['frame']<=b[0]['frame']:why.append('low_flip_not_after_reward_visit')
  if len(switches)>=2 and not switches[-1].get('airborne'):why.append('return_actual_airborne_flip_missing')
 else:lower=[]
 return dict(ok=not why,reasons=why,causal=dict(stonecrown_supported_frames=len(upper),far_reward_visit_frames=len(b),lower_return_supported_frames=len(lower),pair_switches=switches,final_pair=pair,reward_transactions=len(claimed)),behavior=dict(shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks')))
