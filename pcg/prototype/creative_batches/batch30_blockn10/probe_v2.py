import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from .alternatives_v2 import alternatives
from pcg.prototype.creative_batches.batch30_runtime.script_preflight_v1 import check
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v2 import inspect_sources
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_counter_bindings
from pcg.prototype.creative_batches.batch30_blockbridge.probe_v2 import preflight
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','screen','counters'],default='clean');a=p.parse_args();out=ROOT/'results'/a.name
 checks=dict(scripts=check([rules.RUNNER_SCRIPT,HERE/'main_v1.gd']),blocks=inspect_sources([rules.candidate(0)]),counters=inspect_counter_bindings([rules.candidate(0)],alternatives,18))
 if checks['scripts']['status']!='syntax_checked'or any(checks[k]['status']!='requires_physics'for k in ['blocks','counters']):write(out/'preflight.json',checks);write(out/'summary.json',dict(actual_cases=0,status='needs_design'));return
 select=HERE/'control-selection-v2.json';deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'alternatives_v2.py'];e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);write(out/'preflight.json',checks);preflight(e,[rules.candidate(0)])
 if a.stage=='clean':cases=[rules.candidate(k)for k in [0,1]]
 else:
  c=rules.candidate(json.loads(select.read_text())['control'])
  if a.stage=='screen':cases=[instantiate(c,271129918,l,k)for l in ['mild','moderate']for k in range(6)]
  else:cases=alternatives(c)
 rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']},final={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']})
  if a.stage=='counters':o=common.external_outcome(c,r);v['counter_classification']=common.counter_classification(c,r,q,o)
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],final=v['final'],causal=q['causal'])),flush=True)
 if a.stage=='clean':
  good=[v for v in rows if v['purpose']['ok']]
  if select.exists():raise ValueError('immutablecontrolselection')
  write(select,dict(control=good[0]['case']['rule_parameters']['control']if good else None,before_noise=True,source_run=str(out.relative_to(ROOT.parent))))
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),total=len(rows),stage=a.stage,new_candidates=0))
if __name__=='__main__':main()
