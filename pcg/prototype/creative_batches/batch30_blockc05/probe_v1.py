"""Budgeted genuine Godot probes; no alternate simulator or quality gate."""
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
 if out.exists():raise ValueError('immutable run exists')
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v1.py',HERE.parent/'batch30_c05/alternatives_v1.py',HERE.parent/'batch30_blockbridge/probe_v2.py',Path(common.__file__)]
 select=HERE/('control-selection-v2.json'if rules.__name__.endswith('rules_v2')else'control-selection-v1.json')
 if select.exists():deps.append(select)
 engine=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT)
 if a.stage=='clean':cases=[rules.candidate(0,k,s)for s in ['near','far']for k in range(4)]
 else:
  controls=json.loads(select.read_text())['controls'];bases=[rules.candidate(0,k,s)for s,k in controls.items()]
  if a.stage=='screen':cases=[instantiate(c,271128305,l,k)for c in bases for l in ['mild','moderate']for k in range(6)]
  else:cases=[v for c in bases for v in alternatives(c)]
 preflight(engine,[rules.candidate(0,0,s)for s in ['near','far']]);rows=[]
 for c,r,e in engine.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=e,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id','shot_charges']})
  if a.stage=='counters':
   outcome=common.external_outcome(c,r);classification=common.counter_classification(c,r,q,outcome)
   v.update(external_outcome=outcome,counter_classification=classification)
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],final=v['final'],counter=v.get('counter_classification'))),flush=True)
 if a.stage=='clean':
  selected={}
  for route in ['near','far']:
   good=[v for v in rows if v['case']['route_spec']['id']==route and v['purpose']['ok']]
   if good:selected[route]=good[0]['case']['rule_parameters']['control']
  if select.exists():raise ValueError('immutable control selection')
  write(select,dict(controls=selected,before_perturbation=True,source_run=str(out.relative_to(ROOT.parent))))
 write(out/'summary.json',dict(stage=a.stage,actual_cases=engine.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),full_or_held=False,new_candidates=0))

if __name__=='__main__':main()
