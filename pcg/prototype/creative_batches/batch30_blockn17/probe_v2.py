import argparse,copy,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,ground,settle
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
def main():
 p=argparse.ArgumentParser();p.add_argument('--interface',type=int,default=0,choices=[0,1]);p.add_argument('--name',required=True);a=p.parse_args()
 if a.interface==0:
  cs=[rules.candidate(t,k)for t in ['B','C']for k in [0,1]]
  for kind in ['ordinary-horizontal','walk-horizontal','miss-vertical','ground-preopen-vertical']:
   target='B'if'horizontal'in kind else'C';c=rules.candidate(target,0);c['id']+='-counter-'+kind;c['counterexample_kind']=kind
   if kind=='ordinary-horizontal':c['control_plan'][12]=cmd('wait')
   elif kind=='walk-horizontal':c['control_plan']=copy.deepcopy(c['control_plan'][:8])+[settle(1000),ground(),cmd('wait',20)]
   elif kind=='miss-vertical':c['control_plan'][10]=cmd('shoot',direction=[0,1])
   else:c['control_plan']=copy.deepcopy(c['control_plan'][:8])+[cmd('shoot',aim_cell=dict(kind='bell',id='cross-pair')),ground(),cmd('wait',12)]+copy.deepcopy(c['control_plan'][8:])
   cs.append(c)
 else:cs=[rules.candidate(t,k,1,e)for e in ['A','D']for t in ['B','C']for k in [0,1]]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'core-v2'):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,margin=rules.support_margin(c,r),result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if c.get('counterexample_kind'):row['classification']=counter_classification(c,r,q,external_outcome(c,r),dict(shots=1,jumps=2 if c['route_spec']['to_port']=='B'else 4))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0,new_families=0))
if __name__=='__main__':main()
