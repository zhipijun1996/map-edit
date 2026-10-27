import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_sources
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['clean','noise','counters'],default='clean');a=p.parse_args();source=[c for i in [0,1]for c in rules.layouts(rules.RECIPES[0],i)]
 response=inspect_sources(source)
 if response['status']!='requires_physics':raise ValueError(response)
 if a.mode=='clean':cases=source
 elif a.mode=='noise':cases=[instantiate(c,271027503,l,i)for c in source for l in ['mild','moderate']for i in range(6)]
 else:
  cases=[v for c in source for v in rules.alternatives(c)if v['counterexample_kind'].startswith(('parked-direct-','ordinary-jump-'))or v['counterexample_kind']in ['ground-start-ride-launch','omit-start-shot','omit-final-shot']]
  assert len(cases)==52
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,Path(__file__).with_name('counter-protocol-v1.json')],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,a.mode):
  q=rules.purpose(c,r);row=dict(id=c['id'],purpose=q,result=dict(ok=r.get('ok'),reason=r.get('reason'),shots=r.get('shots'),jumps=r.get('jumps'),coins=r.get('workshop',{}).get('coins')),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows)))
if __name__=='__main__':main()
