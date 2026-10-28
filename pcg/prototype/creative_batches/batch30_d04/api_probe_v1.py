"""Final registration checks and equal pre-calibration noise, not holdout."""
import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from . import api_v1 as api
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--noise',action='store_true');p.add_argument('--counters',action='store_true');a=p.parse_args()
e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(api.__file__)]+api.SOURCE_DEPENDENCIES)
bases=[c for i in range(2)for c in api.layouts(api.RECIPES[0],i)+api.fixtures(i)]
if a.noise:cs=[instantiate(c,261026904,l,j)for c in bases for l in ['mild','moderate']for j in range(6)]
elif a.counters:
 cs=[]
 for c in api.fixtures(0):
  alts=api.alternatives(c)
  cs += [v for v in alts if v['counterexample_kind']in ['omit-shot-6','shore-prepark-extra-shot-80','shore-prepark-extra-shot-100','shore-prepark-extra-shot-150','shore-prepark-extra-shot-170','wrong-park-timing--35','wrong-park-timing-35']]
else:cs=bases
rows=[]
for c,r,ev in e.run(cs,'d04-api-noise'if a.noise else'd04-full-loop-counter'if a.counters else'd04-api-clean'):
 q=api.purpose(c,r);o=api.external_outcome(c,r);row=dict(id=c['id'],ok=q['ok'],purpose=q,external_outcome=o,reason=r.get('reason'),shots=r.get('shots'),ticks=r.get('ticks'),coins=r.get('workshop',{}).get('coins'),evidence=ev);rows.append(row);print(json.dumps(dict(id=c['id'],ok=q['ok'],reason=q['reasons'],world=o,shots=r.get('shots'),ticks=r.get('ticks'))),flush=True)
write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(r['ok']for r in rows),rows=rows))
