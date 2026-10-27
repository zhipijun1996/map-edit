import argparse,json
from pathlib import Path
from . import rules_v3 as rules
from .alternatives_v1 import alternatives
from .probe_v1 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def external(c,r):
 claimed={e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')}
 return bool(r.get('ok'))and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])and set(c['required_rewards'])<=claimed
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--interface',type=int,choices=[0,1],required=True);p.add_argument('--control',type=int,required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'alternatives_v1.py',HERE/'probe_v1.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,e in engine.run(alternatives(rules.candidate(a.interface,a.control)),'exact-goal-counters'):
  q=rules.purpose(c,r);row=compact(c,r,e,q);row['same_external_goal']=external(c,r);row['purpose_difference']=row['same_external_goal']and not q['ok'];rows.append(row)
  print(json.dumps(dict(id=c['id'],goal=row['same_external_goal'],purpose=q['ok'],why=q['reasons'],shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'))),flush=True)
 write(engine.out/'counter-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases,goal_only_differences=[v['case']['id']for v in rows if v['purpose_difference']])),flush=True)
if __name__=='__main__':main()
