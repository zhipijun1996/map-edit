import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from .probe_v1 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'probe_v1.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[];chosen=[]
 for c,r,e in engine.run([rules.candidate(0,k)for k in range(4)],'brake-clean'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q))
  if q['ok']and len(chosen)<2:chosen.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],contact=q['causal']['wall_contact_frames'],preimpact=q['causal'].get('preimpact_velocity'),shots=r.get('shots'),jumps=r.get('jumps'))),flush=True)
 write(engine.out/'selection-before-perturb.json',dict(ids=[c['id']for c in chosen],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031301,l,k)for c in chosen for l in ['mild','moderate']for k in range(6)],'brake-perturb'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 scores=[]
 for c in chosen:
  n={l:sum(v['purpose']['ok']for v in rows if v['case']['id'].startswith(c['id']+'-'+l+'-'))for l in ['mild','moderate']}
  if n['mild']>=5 and n['moderate']>=4:scores.append((-min(n.values()),-sum(n.values()),c['rule_parameters']['control']))
 write(engine.out/'screen-results.json',rows);write(engine.out/'control-selection.json',dict(control=min(scores)[2]if scores else None,holdout_used=False,actual_cases=engine.sim.cases))
 print(json.dumps(dict(actual_cases=engine.sim.cases,controls=scores)),flush=True)
if __name__=='__main__':main()
