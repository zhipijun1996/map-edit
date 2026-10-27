import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','noise'],default='clean');p.add_argument('--control',type=int,default=0);a=p.parse_args()
 cs=[rules.candidate('B',k)for k in [0,2]]+[rules.candidate('C',k)for k in range(4)]if a.stage=='clean'else[instantiate(rules.candidate(t,a.control),271030503,l,k)for t in ['B','C']for l in ['mild','moderate']for k in range(6)]
 assert all(p['initial_phase']==0 for c in cs for p in c['moving_platforms'])
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
