import copy,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write

def cases():
 out=[]
 for i in range(8):
  c=base('n03-cell-'+str(i));c['platforms']=[[-512,900,2048,64]]
  x=760 if i==3 else 256 if i in [4,5]else 512;dwell=1.0 if i==5 else .2;direction=-1 if i==4 else 1
  rules.machinery(c,initial_x=x,speed=120,dwell=dwell,direction=direction,offset=(0,-80),finish=768)
  c.update(spawn=[x,452],entry_port=[x,452],exit_port=[x,452],goal=[-512,400,2048,100],max_frames=300,trace_all=True,id='b31-n03-cell-v1-'+str(i),test_kind=i)
  shot=lambda after=0:cmd('shoot',after,aim_cell=dict(kind='bell',id='reverse-bell'))
  c['control_plan']=[cmd('axis',value=0)]
  if i in [1,2]:c['control_plan']+=([cmd('jump'),cmd('jump_release',20),shot(6)]if i==2 else[shot(20)])
  if i in [3,4]:c['control_plan']+=[shot(120 if i==3 else 60)]
  if i==5:c['control_plan']+=[shot(20),shot(80)]
  if i==6:c['control_plan']+=[shot(20),shot(0)]
  if i==7:c['control_plan']+=[cmd('shoot',20,direction=[1,0])]
  out.append(c)
 return out

def check(c,r):
 fs=r.get('frames',[]);states=r.get('workshop',{}).get('reverse_carriers',[]);s=states[0]if states else{};events=s.get('events',[]);expected=2 if c['test_kind']==5 else 0 if c['test_kind']in[0,7]else 1;why=[]
 if len(events)!=expected:why.append('wrong_actual_reversal_count')
 if any(e['position_before']!=e['position_after']for e in events):why.append('noncontinuous_hit')
 if r.get('hp')!=5 or r.get('returns')or r.get('air_jumps')or r.get('wall_jumps'):why.append('actor_contract_violation')
 sup=[f for f in fs if f.get('support_id')=='reverse-carrier'];neutral=[f for f in sup if abs(f['axis'])<.01]
 if len(neutral)<12:why.append('no_real_neutral_carriage')
 first=events[0]['frame']if events else None;back=[f for f in fs if first is not None and f['frame']>first and any(v['physics_velocity'][0]<-1 for v in f.get('workshop',{}).get('reverse_carriers',[]))]
 if c['test_kind']in [1,2,3,6]and not back:why.append('no_real_velocity_reversal')
 if c['test_kind']==2 and not any(first is not None and f['frame']>first and f.get('support_id')=='reverse-carrier'for f in fs):why.append('no_real_air_catch')
 return dict(ok=not why,reasons=why,actual_reversals=len(events),actual_shots=r.get('shots'),neutral_support_frames=len(neutral),west_velocity_frames=len(back),events=events,engine_reason=r.get('reason'),note='Cell unit scenario; broad goal/raw stable status is not Module admission')

def main():
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn03-cell-v1',extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases(),'cell'):
  row=dict(id=c['id'],check=check(c,r),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
