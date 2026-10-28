import json
from pathlib import Path
from . import rules_v2 as rules,probe_v1 as original
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
def main():
 cs=[rules.metadata(c)for c in original.first8()]
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn16-core-v2',extra_sources=[Path(__file__),Path(original.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'first-eight-v2'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if c.get('counterexample_kind'):row['classification']=counter_classification(c,r,q,external_outcome(c,r),dict(shots=1,jumps=1))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0,new_families=0))
if __name__=='__main__':main()
