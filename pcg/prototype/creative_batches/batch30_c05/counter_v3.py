import argparse,json
from pathlib import Path
from . import rules_v3 as rules
from .alternatives_v1 import alternatives
from .probe_v2 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def outcome(c,r):
 goal=bool(r.get('ok'))and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
 claimed={e['id']for e in r.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')};goal=goal and set(c['required_rewards'])<=claimed
 pairs={p['id']:p for p in r.get('workshop',{}).get('paired_gates',[])};world=all(all(pairs.get(s['id'],{}).get(k)==v for k,v in s.items()if k!='id')for s in c['required_pair_states'])
 return dict(goal_only=goal,required_pair_world=world,same_world_goal=goal and world)
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--interface',type=int,choices=[0,1],required=True);p.add_argument('--near',type=int,required=True);p.add_argument('--far',type=int,required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'alternatives_v1.py',HERE/'probe_v2.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,e in engine.run([v for route,control in [('near',a.near),('far',a.far)]for v in alternatives(rules.candidate(a.interface,control,route))],'exact-goal-and-state-counters'):
  q=rules.purpose(c,r);o=outcome(c,r);row=compact(c,r,e,q);row.update(external_outcome=o,invalidates_declared_mechanism=o['same_world_goal']and not q['ok'],goal_only_world_difference=o['goal_only']and not o['required_pair_world']);rows.append(row)
  print(json.dumps(dict(id=c['id'],goal_only=o['goal_only'],same_world=o['same_world_goal'],purpose=q['ok'],why=q['reasons'],shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'))),flush=True)
 write(engine.out/'counter-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases,refutations=[r['case']['id']for r in rows if r['invalidates_declared_mechanism']],goal_only_world_differences=[r['case']['id']for r in rows if r['goal_only_world_difference']])),flush=True)
if __name__=='__main__':main()
