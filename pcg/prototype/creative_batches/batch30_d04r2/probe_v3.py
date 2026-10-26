import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
from . import rules_v1 as rules
from . import counter_rules_v1 as counters

p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),Path(counters.__file__),Path(classify.__code__.co_filename),Path(__file__).parent/'protocol-v3.json']+rules.SOURCE_DEPENDENCIES)
cs=rules.counters(1)+counters.extra(0)
write(e.out/'protocol.json',dict(maximum_cases=40,prior_probes=72,scope='actual cheap-C policies in exact east160 world; no holdout'))
write(e.out/'cases.json',dict(cases=cs));rows=[]
for c,raw,ev in e.run(cs,'east160-extra-falsifiers'):
 r,audit=classify(c,raw);o=rules.task_outcome(c,r);q=rules.purpose(c,r)
 row=dict(id=c['id'],same_task=o,purpose=q,shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'),coins=r.get('workshop',{}).get('coins'),reason=r.get('reason'),evidence=ev,observer_interpretation=audit)
 rows.append(row);print(json.dumps({k:v for k,v in row.items()if k not in ['purpose','evidence','observer_interpretation']}),flush=True)
write(e.out/'summary.json',dict(actual_cases=e.sim.cases,same_task_successes=[x for x in rows if x['same_task']['ok']],rows=rows))
