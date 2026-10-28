import copy,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
HERE=Path(__file__).parent

def main():
 cs=[rules.candidate(t,k)for t in ['B','C']for k in range(3)]
 for target in ['B','C']:
  c=rules.candidate(target,0);c['id']+='-counter-ordinary-no-shot';c['counterexample_kind']='ordinary-no-shot';c['control_plan']=[cmd('axis',value=1),wait_x(228),cmd('jump'),cmd('jump_release',20),settle(c['exit_port'][0]),dict(op='wait',trigger=dict(state='grounded',timeout=240)),cmd('wait',20)];cs.append(c)
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn12-core-v1',extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'first-eight-core'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,margin=rules.margin(c,r),result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if c.get('counterexample_kind'):row['classification']=counter_classification(c,r,q,external_outcome(c,r),dict(shots=1,jumps=1))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0))
if __name__=='__main__':main()
