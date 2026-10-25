import json,copy
from pathlib import Path
from pcg.prototype.creative_batches.machinery.probe_v1 import platform,board
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle,wait_x,reward,finish
from pcg.prototype.dynamic.generators import dynamic as dyn

def candidates():
 out=[]
 for phase in [.44,.46]:
  c=base('lift-v2-'+str(phase));c['family']='elevator-headroom';c['platforms']+=[[380,65,270,100],[240,-100,410,50]];c['moving_platforms']=[platform('carrier',[310,448],[310,50],2.2,1.2)]
  p=board()+[dyn('wait','platform_phase',query=dict(id='carrier',window=[phase,phase+.02]),timeout=900),cmd('axis',value=1),settle(530,6)]
  reward(c,530,47);finish(c,530,47,p);c['trace_all']=True;c['max_frames']=1500;out.append(c)
 for phase in [.46,.48]:
  c=base('transfer-v2-'+str(phase));c['family']='carrier-rendezvous';c['platforms']+=[[1260,438,230,100]];c['moving_platforms']=[platform('carrier',[300,448],[650,448],2.,1.2),platform('other',[850,448],[1000,448],2.,1.2)]
  p=board()+[dyn('wait','platform_phase',query=dict(id='carrier',window=[phase,phase+.02]),timeout=900),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),dyn('wait','on_platform',query=dict(id='other'),timeout=180),cmd('axis',value=0),cmd('wait',after=20),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(1370,6)]
  reward(c,1370,420);finish(c,1370,420,p);c['trace_all']=True;c['max_frames']=1700;out.append(c)
 for phase in [.88,.9,.92]:
  c=base('pursuit-v2-'+str(phase));c['family']='saw-pursuit';c['platforms']=[[-160,438,860,100],[700,565,540,100],[240,250,460,125]];c['saws']=[dict(source_id='pursuer',origin=[560,414],travel=[300,0],radius=24,period=6.,initial_phase=0.,damage=1,contact_interval=.7)]
  p=[cmd('axis',value=1),wait_x(180),cmd('axis',value=0),dyn('wait','saw_phase',query=dict(id='pursuer',window=[phase,phase+.02]),timeout=900),cmd('axis',value=1),settle(1030,after=6)]
  reward(c,1030,547);finish(c,1030,547,p);c['trace_all']=True;c['max_frames']=1300;out.append(c)
 for pausex in [490,520]:
  c=base('park-v2-'+str(pausex));c['family']='park-return';c['platforms']+=[[650,200,160,60],[1260,438,230,100]];c['moving_platforms']=[platform('carrier',[300,448],[1000,448],3.,1.)]
  c['latches']=[dict(id='park-bell',bell=[300,330],gate=[-100,100,10,10],open_seconds=0,ferry_id='carrier',return_access=[680,300])]
  p=[cmd('axis',value=1),wait_x(210),cmd('jump'),cmd('jump_release',after=10),dyn('wait','on_platform',query=dict(id='carrier'),timeout=180),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='bell',id='park-bell')),dyn('wait','actor_x',query=dict(direction='gte',value=pausex),timeout=400),cmd('shoot',aim_cell=dict(kind='bell',id='park-bell',receiver='access')),cmd('wait',after=12),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.5,.8660254]),settle(720,6),dict(op='wait',trigger=dict(state='grounded',timeout=180)),cmd('axis',value=-1),wait_x(620,-1),cmd('axis',value=0),dyn('wait','on_platform',query=dict(id='carrier'),timeout=180),cmd('shoot',aim_cell=dict(kind='bell',id='park-bell',receiver='access')),dyn('wait','actor_x',query=dict(direction='gte',value=1000),timeout=500),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(1370,6)]
  reward(c,720,182);finish(c,1370,420,p);c['trace_all']=True;c['max_frames']=1900;out.append(c)
 return out
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v2';e=WorkshopEngine(out,extra_sources=[Path(__file__),Path(__file__).with_name('probe_v1.py')]);rows=[]
 for c,r,ev in e.run(candidates(),'geometry-probe'):
  frames=r.get('frames',[]);row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),error=r.get('plan_error'),supports=list({f.get('support_id')for f in frames}),hp=r.get('hp'),coins=r.get('workshop',{}).get('coins'),shots=r.get('shots'),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
