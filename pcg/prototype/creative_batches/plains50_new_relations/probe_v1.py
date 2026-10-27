"""Bounded probes for four recoil/world-state hypotheses, not admitted content."""
import copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish,brake,launch
from pcg.prototype.dynamic.generators import dynamic
from pcg.prototype.creative_batches.descending_carrier.probe_v1 import candidates as old_descent
HERE=Path(__file__).parent

def brake_gate(v=0):
 c=brake(v);c['id']=f'p50-brake-gate-{v}';c['family']='brake-gate-catch'
 c['latches']=[dict(id='pocket-bell',bell=[650+v*20,339+v*0],gate=[180,290,20,170+v*30],open_seconds=.9,return_access=[70,360+v*30])]
 p=c['control_plan'];p[2]=cmd('shoot',aim_cell=dict(kind='bell',id='pocket-bell'));c['control_plan']=p;c['max_frames']=800
 c['rule_parameters']=dict(c['rule_parameters'],relationship='same airborne shot opens pocket while braking into it');return c

def crate(v=0,delay=16):
 c=base(f'p50-sliding-support-{v}-{delay}');c['family']='shoot-slide-catch'
 c['platforms']=[[-160,438,400,100],[900+v*30,438-v*10,250,100],[-200,820,1500,60]]
 c['moving_platforms']=[dict(platform_id='sliding-crate',start=[330,610],finish=[450+v*20,610],size=[144,22],travel_duration=.8,dwell_duration=.15,initial_phase=0)]
 c['latches']=[dict(id='crate-impact',bell=[248,610],gate=[-100,0,10,10],ferry_id='sliding-crate',open_seconds=0,sliding_support=dict(stop_clock=.95))]
 p=[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',after=8),cmd('shoot',after=delay-8,aim_cell=dict(kind='bell',id='crate-impact')),dynamic('wait','on_platform',query=dict(id='sliding-crate'),timeout=300),cmd('axis',value=1),wait_x(500+v*20),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254037844386]),settle(1010+v*30,6)]
 reward(c,1010+v*30,420-v*10);finish(c,1010+v*30,420-v*10,p);c['max_frames']=1100
 c['rule_parameters']=dict(relationship='one shot pushes support forward while player recoils backward; catch support to recover then jump',receiver_x=900+v*30);return c

def return_park(v=0,wait=45):
 c=base(f'p50-return-park-{v}-{wait}');c['family']='return-platform-investment'
 c['platforms']=[[-160,180,400,100],[640+v*30,180,260,100],[-250,780,1600,60]];c['spawn']=[80,162];c['entry_port']=[80,162]
 c['moving_platforms']=[dict(platform_id='return-step',start=[270,450],finish=[550+v*30,450],size=[144,22],travel_duration=2,dwell_duration=.15,initial_phase=0)]
 c['latches']=[dict(id='park-bell',bell=[125,120],gate=[-100,0,10,10],ferry_id='return-step',open_seconds=0,return_access=[780+v*30,160])]
 reward(c,760+v*30,162)
 p=[cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='park-bell')),cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',after=8),cmd('shoot',after=10,aim_cell=dict(kind='bell',id='park-bell')),settle(760+v*30,6),cmd('wait',after=8),cmd('axis',value=-1),wait_x(610+v*30,-1),dynamic('wait','on_platform',query=dict(id='return-step'),timeout=300),cmd('axis',value=-1),wait_x(340,-1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[.5,.8660254037844386]),settle(140,6)]
 finish(c,140,162,p);c['max_frames']=1400;c['rule_parameters']=dict(relationship='outbound pause preserves lower return support in same world; reward persists',far_shore=640+v*30);return c

def descent(v=0):
 c=copy.deepcopy(old_descent()[0]);c['id']=f'p50-descending-revision-{v}';c['family']='descending-carrier'
 # Original near-shore start/pause line is occluded by a real downward rock tooth.
 # Move the bell behind the tooth so it is only exposed from the departing deck.
 c['latches'][0]['bell']=[540,410+v*15];c['latches'][0].pop('return_access',None)
 c['platforms'].append([245,290,30,105])
 c['control_plan'][1]=wait_x(430);c['rule_parameters']=dict(c['rule_parameters'],bell=[540,410+v*15],near_bank_rock=[245,290,30,105]);return c

def candidates():
 return [brake_gate(v)for v in [0,1]]+[crate(v,d)for v in [0,1]for d in [16,24]]+[return_park(v,d)for v in [0,1]for d in [45]]+[descent(v)for v in [0,1]]
if __name__=='__main__':
 out=ROOT/'results/workshop-plains50-new-probes-v1';e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'runner_v1.gd',HERE/'sliding_support_v1.gd'],runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,ev in e.run(candidates(),'new-relations-probe'):
  fs=r.get('frames',[]);ss=[f for f in fs if f.get('support_id')in ['sliding-crate','return-step','descending-deck']]
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),support_frames=len(ss),last={k:fs[-1].get(k)for k in ['x','y','support_id']}if fs else None,evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
