"""Four preregistered real-body probes for PR-D02; no parallel simulator."""
import copy,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,wait_x,settle,reward,finish
from pcg.prototype.dynamic.generators import dynamic
HERE=Path(__file__).parent

def candidates():
 out=[]
 for retreat in [305,325]:
  for advance in [510,530]:
   c=base(f'descending-carrier-v1-r{retreat}-a{advance}');c['family']='descending-carrier';c['capabilities']=['move','jump','shot_recoil']
   c['platforms']=[[-80,290,320,100],[990,335,240,100],[560,60,160,350],[-430,820,1900,60],[-360,710,120,30],[-210,600,120,30],[-360,490,120,30],[-210,380,120,30]]
   c['spawn']=[80,272];c['entry_port']=[80,272]
   c['moving_platforms']=[dict(platform_id='descending-deck',start=[360,300],finish=[760,600],size=[288,20],travel_duration=3.2,dwell_duration=.15,initial_phase=0)]
   c['latches']=[dict(id='departure-bell',bell=[540,250],gate=[-70,100,10,10],open_seconds=0,ferry_id='descending-deck',return_access=[1100,250])]
   c['thorns']=[dict(surface_id='roof-near-face',platform_index=2,face='left',start_offset=0,length=350,depth=10)]
   p=[cmd('axis',value=1),wait_x(430),dynamic('wait','on_platform',query=dict(id='descending-deck'),timeout=120),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='departure-bell')),cmd('axis',value=-1),wait_x(retreat,-1),cmd('axis',value=0),wait_x(advance),cmd('axis',value=1),wait_x(744),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254037844386]),settle(1100,6)]
   c['rule_parameters']=dict(retreat_x=retreat,forward_read_x=advance,roof=[560,60,160,350],receiver=[990,335,240,100],carrier_drop=300,departure_x=744)
   reward(c,1100,317);finish(c,1100,317,p);c['max_frames']=1000;c['trace_all']=False;c['design_id']='PR-D02';out.append(c)
 return out

def summarize(c,r,e):
 fs=r.get('frames',[]);support=[f for f in fs if f.get('support_id')=='descending-deck'];neutral=[f for f in support if abs(f.get('axis',0))<.01]
 return dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),hp=r.get('hp'),shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),supported_frames=len(support),neutral_supported_frames=len(neutral),supported_drop=max((f['y']for f in support),default=0)-min((f['y']for f in support),default=0),last=({k:fs[-1].get(k)for k in ['frame','x','y','support_id']}if fs else None),accepted=[dict(frame=f['frame'],x=f['x'],y=f['y'],events=f['accepted'])for f in fs if f.get('accepted')],evidence=e)
if __name__=='__main__':
 out=ROOT/'results/workshop-descending-carrier-probe-v1';engine=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'protocol-v1.json']);rows=[]
 for c,r,e in engine.run(candidates(),'descending-carry-probe'):
  row=summarize(c,r,e);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2))
