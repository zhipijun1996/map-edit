import json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
HERE=Path(__file__).parent
def main():
 source=rules.layouts(rules.RECIPES[0],0)[0]
 cases=[v for v in rules.alternatives(source)if v['counterexample_kind'].startswith('preopen-from-supported-top-192-')]
 assert len(cases)==2
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockc06-regression-v2',extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'regression-protocol-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,'early-shot-regression'):
  q=checked_purpose(rules,c,r);o=external_outcome(c,r);cl=counter_classification(c,r,q,o)
  row=dict(id=c['id'],purpose=q,outcome=o,classification=cl,evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,same_external_outcomes=sum(r['outcome']['ok']for r in rows),design_refutations=sum(r['classification']['invalidates_design']for r in rows)))
if __name__=='__main__':main()
