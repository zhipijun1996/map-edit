"""Original Godot/phase engine; compact failure records, no custom solver."""
import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.creative_batches.batch30_blockbridge.probe_v2 import preflight
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','screen'],required=True);a=p.parse_args();out=ROOT/'results'/a.name
 if out.exists():raise ValueError('immutableprobe')
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE.parent/'batch30_blockbridge/probe_v2.py',Path(common.__file__)]
 select=HERE/('control-selection-v2.json'if rules.__name__.endswith('rules_v2')else'control-selection-v1.json')
 if select.exists():deps.append(select)
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT)
 if a.stage=='clean':cases=[rules.candidate(0,k,s)for s in ['high','low']for k in range(4)]
 else:
  chosen=json.loads(select.read_text())['controls'];cases=[instantiate(rules.candidate(0,k,s),271128707,l,j)for s,k in chosen.items()for l in ['mild','moderate']for j in range(6)]
 preflight(e,[rules.candidate(0,0,s)for s in ['high','low']]);rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:(r.get('frames')or[{}])[-1].get(k)for k in ['x','y','support_id']})
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],final=v['final'],causal=q['causal'])),flush=True)
 if a.stage=='clean':
  controls={}
  for s in ['high','low']:
   good=[v for v in rows if v['case']['route_spec']['id']==s and v['purpose']['ok']]
   if good:controls[s]=good[0]['case']['rule_parameters']['control']
  if select.exists():raise ValueError('immutableselection')
  write(select,dict(controls=controls,before_perturbation=True,source_run=str(out.relative_to(ROOT.parent))))
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),new_candidates=0,full_or_held=False))

if __name__=='__main__':main()
