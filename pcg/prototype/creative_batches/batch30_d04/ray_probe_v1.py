"""Read-only geometry falsifiers: can stable far banks freely retime the bell?"""
import copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.rules import cmd
from . import rules_v3 as rules
cs=[]
for port in ['B','C']:
 c=rules.materialize();xy=next(p['position']for p in c['ports']if p['id']==port)
 c.update(id='d04-ray-falsifier-'+port,spawn=xy,entry_port=xy,exit_port=[80,420],goal=[xy[0]-25,xy[1]-4,50,8],control_plan=[cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='return-control')),cmd('wait',80)],max_frames=180)
 cs.append(c)
e=WorkshopEngine(ROOT/'results/workshop-batch30-d04-ground-rays-v1',extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES);rows=[]
for c,r,ev in e.run(cs,'ground-ray-counter'):
 row=dict(id=c['id'],ok=r.get('ok'),toggles=[v for v in r.get('workshop',{}).get('events',[])if v['type']=='carrier_toggle'],reason=r.get('reason'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
write(e.out/'summary.json',rows)
