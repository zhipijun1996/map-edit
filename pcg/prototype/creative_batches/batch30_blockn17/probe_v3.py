import json
from pathlib import Path
from . import rules_v2 as rules,critical_v1 as critical
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
HERE=Path(__file__).parent
def main():
 b0=rules.candidate('B',1);c0=rules.candidate('C',0);c1=rules.candidate('C',0,1);db=rules.candidate('B',1,1,'D');dc=rules.candidate('C',0,1,'D')
 cs=[critical.via_B(c0),critical.via_B(c1),critical.direct_D(db),critical.via_B(dc,True),critical.preopen(c0)]
 v=critical.variant(b0,'omit-horizontal-shot',b0['control_plan']);v['control_plan'][12]=cmd('wait');cs.append(v)
 v=critical.direct_D(db,'direct-D-ordinary-no-shot');v['control_plan'][7]=cmd('wait');cs.append(v)
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn17-critical-v1',extra_sources=[Path(__file__),Path(critical.__file__),HERE/'control-selection-v1.json',*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'critical-before-noise'):
  q=checked_purpose(rules,c,r);o=external_outcome(c,r);base=dict(shots=2 if c['route_spec']['from_port']=='D'else 1,jumps=2 if c['route_spec']['to_port']=='B'else 4)
  row=dict(id=c['id'],purpose=q,outcome=o,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},classification=counter_classification(c,r,q,o,base),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,new_modules=0,new_families=0))
if __name__=='__main__':main()
