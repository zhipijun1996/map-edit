import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','noise','counters'],default='clean');a=p.parse_args()
 source=rules.layouts(rules.RECIPES[0],1)
 if a.stage=='clean':
  paid=rules.candidate('C',True);paid['id']+='-paid-control';cases=source+[paid]
 elif a.stage=='noise':cases=[instantiate(c,271029103,l,i)for c in source for l in ['mild','moderate']for i in range(6)]
 else:cases=[v for c in source for v in rules.alternatives(c)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],case=c,purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if a.stage=='counters':
   from pcg.prototype.creative_batches.batch30_blockn04.counter_policy_v1 import classify
   row['classification']=classify(c,r,q,external_outcome(c,r),dict(shots=2 if c['rule_parameters']['target']=='B'else 1,jumps=2))
  rows.append(row);print(json.dumps(dict(id=c['id'],purpose=q,result=row['result'],classification=row.get('classification'))),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows),design_refutations=sum(r.get('classification',{}).get('invalidates_design',False)for r in rows),rows=rows,new_modules=0))
if __name__=='__main__':main()
