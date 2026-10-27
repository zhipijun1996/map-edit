import json
from pathlib import Path
from . import api_v1 as api
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome

def main():
 c=next(v for v in api.alternatives(api.layouts(api.RECIPES[0],0)[1])if v['counterexample_kind']=='old-upper-return-0866')
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn08-fresh-bonus-counter-v1',extra_sources=[Path(__file__),Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([c],'fresh-B-bonus'):
  q=checked_purpose(api,c,r);o=external_outcome(c,r);cl=api.COUNTER_CLASSIFIER(c,r,q,o,dict(shots=1,jumps=1));row=dict(id=c['id'],purpose=q,outcome=o,classification=cl,actual_coins=r.get('workshop',{}).get('coins'),first_frame_coins=r['frames'][0]['workshop']['coins'],claims=[x for x in r['workshop']['events']if x.get('type')=='chest_claim'],evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
