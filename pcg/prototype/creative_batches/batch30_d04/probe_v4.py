import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from . import rules_v4 as rules
p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--route',default='outbound');p.add_argument('--park',default='middle');a=p.parse_args()
e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES);rows=[]
for c,r,ev in e.run([rules.materialize(0,a.park,a.route,i)for i in range(4)],'d04-core-probe'):
 fs=r.get('frames',[]);q=rules.purpose(c,r);row=dict(id=c['id'],ok=q['ok'],reason=r.get('reason'),purpose=q,shots=r.get('shots'),last={k:fs[-1].get(k)for k in ['frame','x','y','support_id']}if fs else{},accepted=[dict(frame=f['frame'],x=f['x'],y=f['y'],events=f['accepted'])for f in fs if f.get('accepted')],fired=r.get('fired_commands'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
write(e.out/'summary.json',dict(actual_cases=e.sim.cases,rows=rows))
