"""One bounded cheap-policy batch on the exact first PR-D02 probe geometry."""
import copy,json
from pathlib import Path
from pcg.prototype.creative_batches.descending_carrier.probe_v1 import candidates,summarize
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.dynamic.generators import dynamic
HERE=Path(__file__).parent

def alternatives():
 base=candidates()[0];out=[]
 def add(label,plan):
  c=copy.deepcopy(base);c['id']+='-counter-'+label;c['counterexample_kind']=label;c['control_plan']=plan;out.append(c)
 # Native world/support relation is assessed from the trace, never axis words.
 add('no-reverse',copy.deepcopy(base['control_plan'][:5])+[cmd('axis',value=0)]+copy.deepcopy(base['control_plan'][8:]))
 for x in [280,320,360]:
  p=copy.deepcopy(base['control_plan']);p[1]=wait_x(x);p[5:8]=[cmd('axis',value=0)];add('rear-board-'+str(x),p)
 for delay in [90,120,150]:
  p=copy.deepcopy(base['control_plan'][:5])+[cmd('axis',value=0),cmd('wait',after=delay),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254037844386]),settle(1100,6)];add('neutral-then-jump-'+str(delay),p)
 # Start and pause from the real original entry bank, then attempt to board the
 # stopped platform. Downward/horizontal recoil are both tried, with no geometry
 # changes and original ammunition recovery only.
 for delay in [110,130,150]:
  for label,aim in [('horizontal',[-1,0]),('downward',[-.8,-.6])]:
   p=[cmd('axis',value=1),wait_x(220),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='departure-bell')),cmd('shoot',after=delay,aim_cell=dict(kind='bell',id='departure-bell')),cmd('axis',value=1),wait_x(220),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=aim),dynamic('wait','on_platform',query=dict(id='descending-deck'),timeout=180),cmd('axis',value=1),wait_x(744),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254037844386]),settle(1100,6)]
   add('shore-prepark-'+str(delay)+'-'+label,p)
 return out

def causal_metrics(r):
 fs=r.get('frames',[]);supported=[f for f in fs if f.get('support_id')=='descending-deck'];motion=[];rel=[]
 for f in supported:
  p=next((p for p in f.get('moving_platforms',[])if p['id']=='descending-deck'),None)
  if p:
   rel.append(dict(frame=f['frame'],relative_x=f['x']-p['position'][0],platform_y=p['position'][1]))
   if p.get('physics_velocity',[0,0])[1]>10:motion.append(f)
 shots=[f for f in fs if any(e['type']=='shot'for e in f.get('accepted',[]))];first=shots[0]if shots else None;around=[]
 if first:
  for f in fs:
   if first['frame']-1<=f['frame']<=first['frame']+12:
    p=next((p for p in f.get('moving_platforms',[])if p['id']=='descending-deck'),None)
    if p:around.append(dict(frame=f['frame'],x=f['x'],y=f['y'],relative_x=f['x']-p['position'][0],support=f.get('support_id')))
 return dict(moving_supported_frames=len(motion),moving_supported_drop=max((f['y']for f in motion),default=0)-min((f['y']for f in motion),default=0),relative_x_range=[min((v['relative_x']for v in rel),default=None),max((v['relative_x']for v in rel),default=None)],first_shot_window=around,relative_first_shot_dx=(around[-1]['relative_x']-around[0]['relative_x']if around else None))
if __name__=='__main__':
 out=ROOT/'results/workshop-descending-carrier-counters-v1';e=WorkshopEngine(out,extra_sources=[Path(__file__),HERE/'probe_v1.py',HERE/'protocol-v1.json']);rows=[]
 for c,r,ev in e.run(alternatives(),'cheap-policy'):
  row=summarize(c,r,ev);row.update(kind=c['counterexample_kind'],causal=causal_metrics(r));rows.append(row);print(json.dumps(dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),moving_supported_frames=row['causal']['moving_supported_frames'],moving_supported_drop=row['causal']['moving_supported_drop'])),flush=True)
 (out/'summary.json').write_text(json.dumps(dict(schema='pcg/descending-carrier-cheap-policies/v1',exact_geometry_source='workshop-descending-carrier-probe-v1',cases=len(rows),safe_goal_arrivals=sum(bool(r['ok'])for r in rows),rows=rows,new_candidates=0,production_admitted=False),ensure_ascii=False,indent=2))
