import json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
HERE=Path(__file__).parent
def main():
 sel=HERE/'control-selection-v1.json';s=json.loads(sel.read_text());bases=[rules.candidate(t,s['controls']['0']['A-'+t])for t in ['B','C']];cs=[instantiate(c,271131727,l,k)for c in bases for l in ['mild','moderate']for k in range(3)]
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn17-noise-v1',extra_sources=[Path(__file__),sel,*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'threeport-noise'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0,new_families=0))
if __name__=='__main__':main()
