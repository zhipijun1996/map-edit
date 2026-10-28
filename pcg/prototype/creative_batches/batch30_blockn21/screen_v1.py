"""Frozen two-branch normal noise, original inputs and sources."""
import argparse,json
from pathlib import Path
from . import control_v2 as control
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
DEPS=[HERE/n for n in ['control_v1.py','control_v2.py','control-flow-domain-v1.json','control-flow-domain-v2.json','control-selection-v1.json','settle-failure-feedback-v1.json']]+[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES]
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();out=ROOT/'results'/a.name
 cs=[instantiate(control.candidate(target,0),271130131,l,k)for target in ['B','C']for l in ['mild','moderate']for k in range(6)]
 e=WorkshopEngine(out,extra_sources=[Path(__file__),*DEPS],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'frozen-two-branch-noise'):
  q=rules.purpose(c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'])),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,prior_cases=22,new_candidates=0,passed=sum(v['purpose']['ok']for v in rows)))
if __name__=='__main__':main()
