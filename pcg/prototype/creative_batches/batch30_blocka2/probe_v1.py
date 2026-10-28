import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','noise'],default='clean');a=p.parse_args()
 if a.stage=='clean':cs=[rules.candidate(i,'out')for i in [0,1]]+[rules.candidate(i,'back',h)for i in [0,1]for h in [20,24,28]]
 else:cs=[instantiate(c,271029703,l,t)for i in [0,1]for c in rules.layouts(rules.RECIPES[0],i)for l in ['mild','moderate']for t in range(3)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows))
if __name__=='__main__':main()
