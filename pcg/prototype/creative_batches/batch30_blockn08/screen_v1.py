import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['directions','noise'],default='directions');a=p.parse_args();sel=HERE/'control-selection-v1.json';k=json.loads(sel.read_text())['chosen_control'];assert k is not None
 cs=[rules.candidate(k,route)for route in ['out','back']]
 if a.stage=='noise':cs=[instantiate(rules.candidate(k,route),271130820,l,j)for route in ['out','back','loop']for l in ['mild','moderate']for j in range(3)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),sel,*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
