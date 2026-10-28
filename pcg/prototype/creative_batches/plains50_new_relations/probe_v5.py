"""Second ground-detour revision: wait for actual arrival and ground recovery."""
import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.plains50_new_relations.probe_v4 import ground_detour
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import cmd,wait_x
HERE=Path(__file__).parent

def detour2(v=0,dy=.7):
 c=ground_detour(v,dy);c['id']=c['id'].replace('p50-','p50-v2-');front=c['rule_parameters']['intermediate'][0]
 p=c['control_plan'];p[6:6]=[wait_x(front+100),dict(op='wait',trigger=dict(state='grounded',timeout=240))]
 c['rule_parameters'].update(revision='settle sets steering and does not itself wait; bind onward move to actual island arrival and grounding');return c
if __name__=='__main__':
 out=ROOT/'results/workshop-plains50-new-probes-v5';e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'probe_v4.py']);rows=[]
 for c,r,ev in e.run([detour2(v,d)for v in [0,1]for d in [.7,.8660254037844386]],'ground-detour-revision2'):
  fs=r.get('frames',[]);row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),accepted=[dict(frame=f['frame'],x=f['x'],y=f['y'],events=f['accepted'])for f in fs if f.get('accepted')],last={k:fs[-1].get(k)for k in ['x','y','support_id']}if fs else None,evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
