import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.block_contract_v1 import inspect_sources
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['clean','noise','counters'],default='clean');a=p.parse_args()
 source=rules.layouts(rules.RECIPES[0],0);response=inspect_sources(source)
 if response['status']!='requires_physics':raise ValueError(response)
 if a.mode=='clean':cases=source
 elif a.mode=='noise':cases=[instantiate(c,271027303,level,i)for c in source for level in ['mild','moderate']for i in range(6)]
 else:cases=[v for c in source for v in rules.alternatives(c)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT)
 rows=[]
 for c,r,ev in e.run(cases,a.mode):
  q=rules.purpose(c,r);row=dict(id=c['id'],purpose=q,result=dict(ok=r.get('ok'),reason=r.get('reason'),shots=r.get('shots'),jumps=r.get('jumps'),final=r.get('final')),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows)))
if __name__=='__main__':main()
