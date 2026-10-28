import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
from . import rules_v1 as rules

p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),Path(classify.__code__.co_filename)]+rules.SOURCE_DEPENDENCIES)
cs=rules.cases(0)+rules.counters(0)
write(e.out/'protocol.json',dict(maximum_cases=20,root='pcg/creative-production/batch30/protocol-v7.json',scope='new D04 east160 initial core and adaptive same-task falsifiers; no holdout'))
write(e.out/'cases.json',dict(cases=cs))
rows=[]
for c,raw,ev in e.run(cs,'east160-core-and-falsifier'):
 r,audit=classify(c,raw);q=rules.purpose(c,r);o=rules.task_outcome(c,r)
 row=dict(id=c['id'],nominal='counterexample_kind'not in c,purpose=q,same_task=o,shots=r.get('shots'),jumps=r.get('jumps'),ticks=r.get('ticks'),coins=r.get('workshop',{}).get('coins'),reason=r.get('reason'),evidence=ev,observer_interpretation=audit)
 rows.append(row);print(json.dumps({k:v for k,v in row.items()if k not in ['purpose','evidence','observer_interpretation']}),flush=True)
write(e.out/'summary.json',dict(actual_cases=e.sim.cases,rows=rows))
