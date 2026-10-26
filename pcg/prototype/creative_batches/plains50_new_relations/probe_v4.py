"""Ground-refill detour proposal: outward to recover, then reverse upward."""
import json,math
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish,launch
HERE=Path(__file__).parent

def ground_detour(v=0,dy=.7):
 c=base(f'p50-ground-detour-{v}-{dy}');c['family']='ground-refill-switchback'
 front=420+v*20;top=300+v*10;high=310+v*20
 c['platforms'] += [[front,top,230,80],[high-90,118,180,70],[-220,720,1500,60]]
 p=launch(12,18,dy,takeoff=205)+[settle(front+105,6),cmd('wait',after=6),cmd('axis',value=-1),wait_x(front+25,-1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[.5,.8660254037844386]),settle(high,6)]
 reward(c,high,100,14);finish(c,high,100,p);c['max_frames']=1200;c['rule_parameters']=dict(relationship='recoil outward to real ground recovery before reverse jump to otherwise too high reward',intermediate=[front,top],high_target=[high,100],first_shot_dy=dy,resource_source='actual original ground contact, no enemy or reset');return c
if __name__=='__main__':
 out=ROOT/'results/workshop-plains50-new-probes-v4';e=WorkshopEngine(out,extra_sources=[Path(__file__)]);rows=[]
 for c,r,ev in e.run([ground_detour(v,d)for v in [0,1]for d in [.7,.8660254037844386]],'ground-refill-switchback'):
  fs=r.get('frames',[]);row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),supports=list({f.get('support_id')for f in fs}),last={k:fs[-1].get(k)for k in ['x','y','support_id']}if fs else None,evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
