import json
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v1 import platform
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle,reward,finish
HERE=Path(__file__).parent

def candidates():
 out=[]
 for delay in [80,84,88,92]:
  c=base('dock-v11-'+str(delay));c['family']='carrier-position-key';c['platforms']=[[-160,438,1600,100]];c['moving_platforms']=[platform('key-carrier',[300,100],[700,100],2.,.5,size=(60,20))];c['latches']=[dict(id='key-control',bell=[200,380],gate=[-100,-100,10,10],open_seconds=0,ferry_id='key-carrier'),dict(id='dock-gate',bell=[-500,-500],gate=[1000,-250,24,688],open_seconds=.18,carrier_dock=dict(platform_id='key-carrier',rect=[480,85,40,30]))]
  p=[cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='key-control')),cmd('shoot',after=delay,aim_cell=dict(kind='bell',id='key-control')),cmd('axis',value=1),settle(1120,6)]
  reward(c,1120,420);finish(c,1120,420,p);c['trace_all']=True;c['max_frames']=1200;out.append(c)
 return out
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v11';e=WorkshopEngine(out,extra_sources=list(HERE.glob('*.py'))+list(HERE.glob('*v11.gd')),runner_script=HERE/'dock_runner_v11.gd');rows=[]
 for c,r,ev in e.run(candidates(),'dock-probe'):
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),coins=r.get('workshop',{}).get('coins'),events=r.get('plains',{}).get('events'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
