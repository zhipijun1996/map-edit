import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
from . import rules_v1 as rules

p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),Path(classify.__code__.co_filename),Path(__file__).parent/'protocol-v2.json']+rules.SOURCE_DEPENDENCIES)
bases=[c for i in range(2)for c in rules.cases(i)]
cs=rules.cases(1)+[instantiate(c,261030001,l,j)for c in bases for l in ['mild','moderate']for j in range(3)]
write(e.out/'protocol.json',dict(maximum_cases=52,prior_probes=20,root='pcg/creative-production/batch30/protocol-v7.json',scope='east160 two-interface clean/noise adaptation; no holdout'))
write(e.out/'cases.json',dict(cases=cs));rows=[]
for c,raw,ev in e.run(cs,'east160-adaptation-noise'):
 r,audit=classify(c,raw);q=rules.purpose(c,r);o=rules.task_outcome(c,r)
 row=dict(id=c['id'],purpose=q,same_task=o,shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'),coins=r.get('workshop',{}).get('coins'),reason=r.get('reason'),evidence=ev,observer_interpretation=audit)
 rows.append(row);print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],ticks=r.get('ticks'))),flush=True)
write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),rows=rows))
