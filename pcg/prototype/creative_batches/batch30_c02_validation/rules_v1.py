"""Support-confirmed C02 recovery on the exact frozen original geometry."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_c02 import api_v1 as core
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
HERE=Path(__file__).parent
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=core.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(core.__file__),*core.SOURCE_DEPENDENCIES,HERE/'runner_v1.gd',HERE/'protocol-v1.json']
LEADS=[4,6,8,10]
def support(c,index,x,timeout=300):
 y=c['platforms'][index][1]-18
 return dict(op='wait',trigger=dict(state='grounded',timeout=timeout,actual_support=dict(id='Platform'+str(index),x_range=[x-4,x+4],y_range=[y-.3,y+.3])))
def pair_a():return dict(op='wait',trigger=dict(state='grounded',timeout=180,actual_pair=dict(id='airlock-pair',open='A')))
def fixture(interface=0,control=0):
 c=core.layouts(core.RECIPES[0],interface)[0];base=copy.deepcopy(c['control_plan']);lead=LEADS[control]
 p=copy.deepcopy(base[:5])+[wait_x(450),cmd('axis',value=0),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='airlock-pair',receiver='access')),pair_a(),cmd('wait',6),settle(-335),support(c,3,-335,480)]
 for index,x in [(4,-430),(5,-340),(6,-250),(7,-160)]:
  p+=[cmd('jump'),settle(x,lead),cmd('jump_release',20-lead),support(c,index,x),cmd('wait',6)]
 p+=[settle(80),support(c,0,80),cmd('wait',8),settle(1000)]+base
 c.update(id=f'b30-c02-recovery-v1-i{interface}-c{control}',control_plan=p,max_frames=2400)
 c['validation_fixture']=dict(kind='intentional_first_swap_miss_restore_original_stairs_retry',module_enrollment=False,world_reset=False,control=control,vertical_lead_ticks=lead,original_core_case=core.layouts(core.RECIPES[0],interface)[0]['id'])
 return c
def purpose(c,r):
 q=core.purpose(c,r);fs=r.get('frames',[]);state=(r.get('workshop',{}).get('paired_gates')or[{}])[0];swaps=[e for e in state.get('events',[])if e.get('type')=='pair_switch'];floor=next((f for f in fs if f.get('grounded')and f.get('support_id')=='Platform3'),None);ordered=[];last=floor['frame']if floor else -1
 for index in [4,5,6,7,0]:
  pos={4:-430,5:-340,6:-250,7:-160,0:80}[index];height=c['platforms'][index][1]-18
  got=next((f for f in fs if f['frame']>last and f.get('grounded')and f.get('support_id')=='Platform'+str(index)and abs(f['x']-pos)<=4 and abs(f['y']-height)<=.3 and sum(abs(v)for v in f.get('real_velocity',[100,100]))<=1),None)
  if got:ordered.append(dict(id='Platform'+str(index),frame=got['frame'],x=got['x'],y=got['y'],shot_charges=got.get('shot_charges'),jumps_used=got.get('jumps_used')));last=got['frame']
 if not floor:q['reasons'].append('actual_first_failure_floor_missing')
 if len(ordered)!=5:q['reasons'].append('actual_centered_stair_A_support_sequence_missing')
 if [e.get('open')for e in swaps]!=['B','A','B']:q['reasons'].append('actual_pair_restore_retry_order_missing')
 if not(len(swaps)==3 and floor and swaps[0]['frame']<floor['frame']<swaps[1]['frame']and ordered and swaps[1]['frame']<ordered[0]['frame']and swaps[1].get('airborne')is False and swaps[2].get('airborne')is True):q['reasons'].append('restore_not_grounded_between_real_failure_and_stairs')
 if ordered and any(p.get('shot_charges',0)<1 for p in ordered):q['reasons'].append('real_landing_resource_renewal_missing')
 violations=[]
 for f in fs:
  pair=(f.get('workshop',{}).get('paired_gates')or[{}])[0];a,b=pair.get('open_a'),pair.get('open_b')
  if not(isinstance(a,bool)and isinstance(b,bool)and a!=b and pair.get('gate_a_layer')==(0 if a else 1)and pair.get('gate_b_layer')==(0 if b else 1)and pair.get('gate_a_disabled')==a and pair.get('gate_b_disabled')==b):violations.append(f['frame'])
 if violations:q['reasons'].append('actual_xor_collision_invariant_failed')
 q['causal'].update(failure_floor_frame=floor['frame']if floor else None,actual_support_sequence=ordered,actual_swaps=swaps,invariant_violations=violations);q['ok']=not q['reasons'];return q
