import json
from pathlib import Path
from . import rules_v2 as rules,counters_v1 as counters
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,counter_classification,external_outcome

def main():
 bases=rules.layouts(rules.RECIPES[0],0);cs=[v for c in bases for v in counters.alternatives(c)[:8]]
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blocka2-counters-v2',extra_sources=[Path(__file__),Path(rules.__file__),Path(counters.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'counters'):
  p=checked_purpose(rules,c,r);o=external_outcome(c,r);cl=counter_classification(c,r,p,o,dict(shots=2 if c['route_spec']['from_port']=='A'else 1,jumps=2));row=dict(id=c['id'],purpose=p,outcome=o,classification=cl,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,design_refutations=[r['id']for r in rows if r['classification']['invalidates_design']],rows=rows))
if __name__=='__main__':main()
