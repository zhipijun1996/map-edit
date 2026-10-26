"""One predeclared four-control domain; select only before independent holdout."""
import argparse,json
from pathlib import Path
from . import api_v2 as api
from . import rules_v7 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--noise',action='store_true');p.add_argument('--interface',type=int,default=0);a=p.parse_args()
bases=[api.prepare(rules.materialize(a.interface,'middle','return-middle',return_control=i))for i in range(4)]
for c in bases:c['required_carrier_park']['x_range']=[515,635]
cs=[instantiate(c,261026904,l,j)for c in bases for l in ['mild','moderate']for j in range(6)]if a.noise else bases
e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(api.__file__),Path(rules.__file__)]+api.SOURCE_DEPENDENCIES+rules.SOURCE_DEPENDENCIES);rows=[]
for c,r,ev in e.run(cs,'v7-return-control-noise'if a.noise else'v7-return-control-clean'):
 q=api.purpose(c,r);row=dict(id=c['id'],ok=q['ok'],purpose=q,reason=r.get('reason'),shots=r.get('shots'),ticks=r.get('ticks'),last={k:r['frames'][-1].get(k)for k in ['x','y','support_id']}if r.get('frames')else{},evidence=ev);rows.append(row);print(json.dumps({k:v for k,v in row.items()if k not in ['evidence','purpose']}),flush=True)
write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(r['ok']for r in rows),rows=rows))
