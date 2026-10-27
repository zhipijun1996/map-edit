import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from .alternatives_v1 import alternatives
from .counter_policy_v1 import classify
from .core_v2 import cases as core_cases
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime import produce_v1 as common
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_counter_bindings
HERE=Path(__file__).parent
def recovery():
 c=core_cases()[5];c.pop('counterexample_kind');c['id']='b30-blockn19-v2-i0-recovery';c['route_spec'].update(id='A-to-B-missed-M-recovery',role='recovery');return c
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['noise','counters','recovery'],required=True);a=p.parse_args();out=ROOT/'results'/a.name;c=rules.candidate(0)
 binding=inspect_counter_bindings([c],alternatives,18)
 if binding['status']!='requires_physics':write(out/'binding.json',binding);raise ValueError('counter geometry binding rejected')
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'core_v1.py',HERE/'core_v2.py',HERE/'alternatives_v1.py',HERE/'counter_policy_v1.py',HERE/'control-selection-v1.json']
 e=WorkshopEngine(out,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT);write(out/'binding.json',binding)
 if a.stage=='noise':cs=[instantiate(c,271130129,l,k)for l in ['mild','moderate']for k in range(12)]
 elif a.stage=='recovery':cs=[instantiate(recovery(),271130229,l,k)for l in ['mild','moderate']for k in range(6)]
 else:cs=alternatives(c)
 rows=[]
 for c,r,ev in e.run(cs,a.stage):
  q=common.checked_purpose(rules,c,r);v=dict(case=c,purpose=q,evidence=ev,actual={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']})
  if a.stage=='counters':v['counter_classification']=classify(c,r,q,common.external_outcome(c,r))
  rows.append(v);write(out/'results.json',rows);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],actual=v['actual'],counter=v.get('counter_classification',{}).get('invalidates_design'))),flush=True)
 write(out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),new_candidates=0))
if __name__=='__main__':main()
