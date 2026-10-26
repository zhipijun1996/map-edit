import argparse,importlib,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
p=argparse.ArgumentParser();p.add_argument('--revision',default='v1');p.add_argument('--name',required=True);a=p.parse_args()
r=importlib.import_module('pcg.prototype.creative_batches.junction_windgap.rules_'+a.revision)
e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(r.__file__),Path(__file__),*r.SOURCE_DEPS]);rows=[]
for c,v,b in e.run([c for i in range(2)for c in r.layouts(r.RECIPES[0],i)],'probe'):
 f=v.get('frames',[]);row=dict(id=c['id'],ok=v.get('ok'),reason=v.get('reason'),purpose=r.purpose(c,v),last={k:f[-1].get(k)for k in ['x','y','frame','support_id']}if f else{},commands=v.get('fired_commands',[]),evidence=b);rows.append(row);print(json.dumps(row),flush=True)
write(e.out/'summary.json',rows)
