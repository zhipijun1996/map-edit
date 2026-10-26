import json
from pathlib import Path
from pcg.prototype.workshop.rules import refund,cmd,settle,reward,finish
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from .probe_v1 import report
HERE=Path(__file__).parent

def cases():
 out=[]
 for top in [80,100]:
  for front in [340,380]:
   c=refund(0);c['id']=f'b30-d03-v2-y{top}-front{front}';c['family']='finite-enemy-route';c['platforms'][1]=[front,top,220,70]
   c['reward_sites']=[];reward(c,front+100,top-18,12)
   plan=[cmd('axis',value=0),cmd('jump'),cmd('axis',6,value=1),cmd('jump_release',10),cmd('shoot',6,aim_cell=dict(kind='enemy',id='ammo-sentry')),cmd('shoot',18,aim_cell=dict(kind='enemy',id='ammo-sentry')),cmd('shoot',18,direction=[0,1]),settle(front+100,6)]
   finish(c,front+100,top-18,plan);c['max_frames']=720;c['trace_all']=False;out.append(c)
 return out
if __name__=='__main__':
 e=WorkshopEngine(ROOT/'results/workshop-batch30-d03-probe-v2',extra_sources=[Path(__file__),HERE/'probe_v1.py',HERE/'protocol-v1.json']);rows=[]
 for c,r,ev in e.run(cases(),'shared-health-lift-revision'):
  row=report(c,r,ev);rows.append(row);print(json.dumps(dict(id=c['id'],**row['summary'])),flush=True)
 write(e.out/'probe-results.json',rows)
