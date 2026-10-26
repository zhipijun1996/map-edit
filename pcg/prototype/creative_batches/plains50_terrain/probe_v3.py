import json
from pathlib import Path
from pcg.prototype.creative_batches.plains50_terrain.production_v3 import materialize,purpose,DEMANDS,HERE
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
if __name__=='__main__':
 e=WorkshopEngine(ROOT/'results/workshop-plains50-terrain-column-probe-v3',extra_sources=[Path(__file__),HERE/'production_v3.py',HERE/'protocol-v1.json']);rows=[]
 cs=[materialize(k,i)for k,d in DEMANDS.items()if d['recipe']=='under-column-escape'for i in range(4)]
 for c,r,ev in e.run(cs,'relay-probe'):
  p=purpose(c,r);fs=r.get('frames',[]);row=dict(id=c['id'],safe=r.get('ok'),reason=r.get('reason'),purpose=p,shots=r.get('shots'),last=({k:fs[-1].get(k)for k in ['frame','x','y','support_id']}if fs else{}),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'summary.json',rows)
