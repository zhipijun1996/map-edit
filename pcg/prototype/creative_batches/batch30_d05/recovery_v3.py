"""Actual missed-bell lower terrain recovery and retry, same world."""
import argparse,copy,json
from pathlib import Path
from . import api_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def fixture(interface=0,control=0):
 c=rules.materialize(interface,1);p=copy.deepcopy(c['control_plan'][:9]);p+=[cmd('shoot',direction=[-.95,.3122498999]),cmd('axis',value=1),wait_x(850),cmd('axis',value=0),ground(),cmd('wait',6),cmd('axis',value=-1),wait_x(-620,-1),cmd('axis',value=0),ground(),cmd('wait',6)]
 for x in [-500,-360,-220,80]:
  p+=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),wait_x(x-4),cmd('axis',value=0),ground(),cmd('wait',6)]
 p+=copy.deepcopy(c['control_plan']);c['control_plan']=p;c['id']+=f'-recovery-c{control}';c['max_frames']=2600;c['validation_fixture']=dict(kind='missed_bell_lower_recovery_retry',module_enrollment=False,world_reset=False)
 return c
def purpose(c,r):
 fs=r.get('frames',[]);floor=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform3'];a=[f for f in fs if floor and f['frame']>floor[-1]['frame']and f.get('grounded')and abs(f['x']-80)<30 and abs(f['y']-420)<1]
 toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle'];retry=bool(a and toggles and toggles[0]['frame']>a[0]['frame']);why=[]
 if not r.get('ok'):why.append(r.get('reason','unstable'))
 if not floor or not a or not retry:why.append('no_same_world_floor_A_retry')
 if r.get('hp')!=5 or r.get('returns'):why.append('harm_or_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<12:why.append('reward_missing')
 return dict(ok=not why,reasons=why,causal=dict(floor_frames=len(floor),actual_return_A=len(a),retry=retry),behavior={})
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--noise',action='store_true');a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT)
 cs=[instantiate(fixture(i),261029019,l,t)for i in [0,1]for l in ['mild','moderate']for t in range(6)]if a.noise else[fixture(i)for i in [0,1]];rows=[]
 for c,r,b in e.run(cs,'missed-bell-real-recovery'):
  q=purpose(c,r);rows.append(dict(case=c,result=r,check=q,evidence=b));print(json.dumps(dict(id=c['id'],check=q,last=[r['frames'][-1].get(k)for k in ['x','y','support_id']])),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['check']['ok']for v in rows),rows=rows))
if __name__=='__main__':main()
