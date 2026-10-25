import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v1 import platform,board
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish
from pcg.prototype.dynamic.generators import dynamic as dyn
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine

def candidates():
 out=[]
 for duration in [2.6,3.0]:
  for leave in [770,800]:
   c=base('evac-v8-'+str(duration)+'-'+str(leave));c['family']='evacuate-rejoin';c['platforms']+=[[650,245,160,60],[1320,438,230,100]];c['moving_platforms']=[platform('carrier',[300,448],[1060,448],duration,1.2)];c['saws']=[dict(source_id='transport-interdict',origin=[750,420],travel=[0,25],radius=40,period=3.2,initial_phase=0,damage=1,contact_interval=.7)]
   p=board()+[wait_x(500),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254]),wait_x(710),cmd('axis',value=0),dict(op='wait',trigger=dict(state='grounded',timeout=180)),cmd('axis',value=1),wait_x(leave),cmd('jump'),cmd('jump_release',after=12),dyn('wait','on_platform',query=dict(id='carrier'),timeout=180),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(1430,6)]
   reward(c,720,227);finish(c,1430,420,p);c['trace_all']=True;c['max_frames']=2000;out.append(c)
 return out
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v8';e=WorkshopEngine(out,extra_sources=list(Path(__file__).parent.glob('*.py')));rows=[]
 for c,r,ev in e.run(candidates(),'evac-probe'):
  row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),coins=r.get('workshop',{}).get('coins'),supports=list({f.get('support_id')for f in r.get('frames',[])}),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
