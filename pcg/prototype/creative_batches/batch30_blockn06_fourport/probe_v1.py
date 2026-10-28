import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','noise'],default='clean');a=p.parse_args()
 if a.stage=='clean':cs=[rules.candidate('A',t,1)for t in ['B','C']]+[rules.candidate('D',t,k)for t in ['B','C']for k in [0,1]]
 else:
  controls=json.loads((HERE/'control-selection-v1.json').read_text())['controls'];cs=[instantiate(rules.candidate(e,t,controls[e+'-'+t]),271130219,l,k)for e in ['A','D']for t in ['B','C']for l in ['mild','moderate']for k in range(6)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},support_margin=rules.support_margin(c,r),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
