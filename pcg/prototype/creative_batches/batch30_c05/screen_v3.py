import argparse,json
from pathlib import Path
from . import rules_v3 as rules
from .probe_v2 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--interface',type=int,choices=[0,1],required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'probe_v2.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[];clean=[]
 for c,r,e in engine.run([rules.candidate(a.interface,k,route)for route in ['near','far']for k in range(4)],'branch-clean'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q))
  if q['ok']:clean.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],shots=r.get('shots'),jumps=r.get('jumps'),last={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})),flush=True)
 chosen=[c for route in ['near','far']for c in [v for v in clean if v['route_spec']['id']==route][:2]]
 write(engine.out/'selection-before-perturb.json',dict(ids=[c['id']for c in chosen],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031201,l,k)for c in chosen for l in ['mild','moderate']for k in range(6)],'branch-perturb'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 winners={}
 for route in ['near','far']:
  scores=[]
  for c in chosen:
   if c['route_spec']['id']!=route:continue
   n={l:sum(v['purpose']['ok']for v in rows if v['case']['id'].startswith(c['id']+'-'+l+'-'))for l in ['mild','moderate']}
   if n['mild']>=5 and n['moderate']>=4:scores.append((-min(n.values()),-sum(n.values()),c['rule_parameters']['control']))
  if scores:winners[route]=min(scores)[2]
 write(engine.out/'screen-results.json',rows);write(engine.out/'control-selection.json',dict(interface=a.interface,controls=winners,holdout_used=False,actual_cases=engine.sim.cases));print(json.dumps(dict(winners=winners,actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
