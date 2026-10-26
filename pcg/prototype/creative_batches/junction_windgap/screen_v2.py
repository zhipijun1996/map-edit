"""Pre-calibration noise and counter probes only, never holdout selection."""
import json
from pathlib import Path
from pcg.prototype.creative_batches.junction_windgap import rules_v2 as r
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
out=ROOT/'results/junction-windgap-screen-v2';e=WorkshopEngine(out,extra_sources=[Path(r.__file__),Path(__file__),*r.SOURCE_DEPS]);rows=[]
cs=[c for i in range(2)for c in r.layouts(r.RECIPES[0],i)]
vs=[instantiate(c,261026606,level,i)for c in cs for level in ['mild','moderate']for i in range(6)]
for c,v,b in e.run(vs,'noise-screen'):
 row=dict(id=c['id'],ok=r.purpose(c,v)['ok'],purpose=r.purpose(c,v),reason=v.get('reason'),evidence=b);rows.append(row)
write(out/'summary.json',dict(probe_cases=e.sim.cases,passed=sum(x['ok']for x in rows),rows=rows,holdout=False))
print(json.dumps(dict(probe_cases=e.sim.cases,passed=sum(x['ok']for x in rows),failures=[x for x in rows if not x['ok']]),ensure_ascii=False),flush=True)
