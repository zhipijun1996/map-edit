import copy,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.rules import cmd,wait_x
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification

def main():
 cs=[rules.candidate(t,k)for t in ['B','C']for k in range(2)]
 for t in ['B','C']:
  for kind in ['wrong-side','omit-shot']:
   c=rules.candidate(t,0);c['id']+='-counter-'+kind;c['counterexample_kind']=kind
   if kind=='omit-shot':c['control_plan'][12]=cmd('wait')
   else:c['control_plan'][10]=cmd('jump_release',4);c['control_plan'][11]=wait_x(400 if t=='B'else 624,-1 if t=='B'else 1)
   cs.append(c)
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn14-core-v1',extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'first-eight'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if c.get('counterexample_kind'):row['classification']=counter_classification(c,r,q,external_outcome(c,r),dict(shots=1,jumps=2))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
