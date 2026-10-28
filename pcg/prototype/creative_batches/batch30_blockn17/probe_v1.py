import copy,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.rules import cmd,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
def main():
 cs=[rules.candidate(t,k)for t in ['B','C']for k in [0,1]]
 for kind in ['ordinary-horizontal','walk-horizontal','miss-vertical','ground-preopen-vertical']:
  target='B'if'horizontal'in kind else'C';c=rules.candidate(target,0);c['id']+='-counter-'+kind;c['counterexample_kind']=kind
  if kind=='ordinary-horizontal':c['control_plan'][12]=cmd('wait')
  elif kind=='walk-horizontal':c['control_plan']=copy.deepcopy(c['control_plan'][:8])+[settle(1000),ground(),cmd('wait',20)]
  elif kind=='miss-vertical':c['control_plan'][10]=cmd('shoot',direction=[0,1])
  else:c['control_plan']=copy.deepcopy(c['control_plan'][:8])+[cmd('shoot',aim_cell=dict(kind='bell',id='cross-pair')),ground(),cmd('wait',12)]+copy.deepcopy(c['control_plan'][8:])
  cs.append(c)
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn17-core-v1',extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'first-eight'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if c.get('counterexample_kind'):row['classification']=counter_classification(c,r,q,external_outcome(c,r),dict(shots=1,jumps=2 if c['route_spec']['to_port']=='B'else 4))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0,new_families=0))
if __name__=='__main__':main()
