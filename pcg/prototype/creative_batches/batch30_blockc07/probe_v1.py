"""Genuine C07 Block probes through original Engine and pair contact observer."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
from pcg.prototype.creative_batches.batch30_blockbridge.probe_v2 import preflight
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','screen','counters'],required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutableprobe')
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE/'counter_policy_v1.py',HERE.parent/'batch30_c07/alternatives_v1.py',HERE.parent/'batch30_blockbridge/probe_v2.py',Path(common.__file__)]
 selection=HERE/('control-selection-v2.json'if rules.__name__.endswith('rules_v2')else'control-selection-v1.json')
 if selection.exists():deps.append(selection)
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT)
 if a.stage=='clean':cases=[rules.candidate(0,k)for k in range(4)]
 else:
  c=rules.candidate(0,json.loads(selection.read_text())['control'])
  cases=[instantiate(c,271128507,l,k)for l in ['mild','moderate']for k in range(6)]if a.stage=='screen'else alternatives(c)
 preflight(e,[rules.candidate(0,0)]);rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})
  if a.stage=='counters':
   from .counter_policy_v1 import classify
   o=common.external_outcome(c,r);v.update(external_outcome=o,counter_classification=classify(c,r,q,o))
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],final=v['final'],counter=v.get('counter_classification'))),flush=True)
 if a.stage=='clean':
  good=[v for v in rows if v['purpose']['ok']]
  if selection.exists():raise ValueError('immutablecontrol')
  write(selection,dict(control=good[0]['case']['rule_parameters']['control']if good else None,before_perturbation=True,source_run=str(out.relative_to(ROOT.parent))))
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),stage=a.stage,new_candidates=0,full_or_held=False))

if __name__=='__main__':main()
