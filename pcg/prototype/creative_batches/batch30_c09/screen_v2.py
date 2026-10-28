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
 for c,r,e in engine.run([rules.candidate(0,k)for k in range(4)],'sameworld-loop-clean'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q))
  if q['ok']and len(chosen)<2:chosen.append(c)
  print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'],causal=q['causal'],last=rows[-1]['actual']['last'],shots=r.get('shots'),jumps=r.get('jumps'))),flush=True)
 write(engine.out/'selection-before-perturb.json',dict(ids=[c['id']for c in chosen],holdout_used=False))
 for c,r,e in engine.run([instantiate(c,261031501,l,k)for c in chosen for l in ['mild','moderate']for k in range(6)],'sameworld-loop-perturb'):
  q=rules.purpose(c,r);rows.append(compact(c,r,e,q));print(json.dumps(dict(id=c['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'screen-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases)),flush=True)
if __name__=='__main__':main()
