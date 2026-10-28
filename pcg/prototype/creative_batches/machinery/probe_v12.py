import json
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v1 import platform
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle,reward,finish,wait_x
from pcg.prototype.dynamic.generators import dynamic as dyn
HERE=Path(__file__).parent

def candidates():
 out=[]
 for delay in [54,60,66,72]:
  c=base('interlock-v12-'+str(delay));c['family']='carrier-dual-service';c['platforms']=[[-160,438,1280,100],[1660,438,240,100]];c['moving_platforms']=[platform('key-carrier',[300,448],[1400,448],3.2,.5,size=(144,20))];c['latches']=[dict(id='key-control',bell=[200,380],gate=[-100,-100,10,10],open_seconds=0,ferry_id='key-carrier',return_access=[1080,360]),dict(id='dock-gate',bell=[-500,-500],gate=[1000,-250,24,688],open_seconds=.18,carrier_dock=dict(platform_id='key-carrier',rect=[480,433,40,30]))]
  p=[cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='key-control')),cmd('shoot',after=delay,aim_cell=dict(kind='bell',id='key-control')),cmd('axis',value=1),wait_x(1065),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='key-control',receiver='access')),cmd('wait',after=100),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),dyn('wait','on_platform',query=dict(id='key-carrier'),timeout=180),cmd('axis',value=0),cmd('wait',after=60),cmd('axis',value=1),wait_x(1450),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(1770,6)]
  reward(c,1770,420);finish(c,1770,420,p);c['trace_all']=True;c['max_frames']=1800;out.append(c)
 return out
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v12';e=WorkshopEngine(out,extra_sources=list(HERE.glob('*.py'))+list(HERE.glob('*v11.gd')),runner_script=HERE/'dock_runner_v11.gd');rows=[]
 for c,r,ev in e.run(candidates(),'interlock-probe'):
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),coins=r.get('workshop',{}).get('coins'),supports=list({f.get('support_id')for f in r.get('frames',[])}),events=r.get('plains',{}).get('events'),evidence=ev);rows.append(row);print(json.dumps({k:v for k,v in row.items()if k!='events'}),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
