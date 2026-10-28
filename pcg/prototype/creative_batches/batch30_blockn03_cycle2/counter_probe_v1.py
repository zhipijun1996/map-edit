import json
from pathlib import Path
from . import rules_v1 as rules,counters_v1 as counters
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification

def main():
 cs=[v for target in ['B','C']for v in counters.alternatives(rules.candidate(target,0))[:8]]
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn03-cycle2-counters-v1',extra_sources=[Path(__file__),Path(counters.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'counter'):
  p=checked_purpose(rules,c,r);o=external_outcome(c,r);cl=counter_classification(c,r,p,o,dict(shots=2 if c['route_spec']['to_port']=='B'else 3,jumps=2 if c['route_spec']['to_port']=='B'else 3));row=dict(id=c['id'],purpose=p,outcome=o,classification=cl,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,design_refutations=[r['id']for r in rows if r['classification']['invalidates_design']],rows=rows))
if __name__=='__main__':main()
