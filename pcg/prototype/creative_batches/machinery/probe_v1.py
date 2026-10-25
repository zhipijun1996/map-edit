import json,copy
from pathlib import Path
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle,wait_x,reward,finish
from pcg.prototype.dynamic.generators import dynamic as dyn

def platform(id,start,finish,duration=2.,dwell=1.,size=(140,20)):
 return dict(platform_id=id,start=start,finish=finish,size=list(size),travel_duration=duration,dwell_duration=dwell,initial_phase=0.)
def board(id='carrier',x=210,window=(0,.02)):
 return [cmd('axis',value=1),wait_x(x),cmd('axis',value=0),dyn('wait','platform_phase',query=dict(id=id,window=list(window)),timeout=900),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=10),dyn('wait','on_platform',query=dict(id=id),timeout=180),cmd('axis',value=0)]
def candidates():
 out=[]
 for phase in [.28,.36]:
  c=base('momentum-'+str(phase));c['family']='momentum-vault';c['platforms']+=[[1060,438,240,100]];c['moving_platforms']=[platform('carrier',[300,448],[760,448],1.6,.8)]
  p=board()+[dyn('wait','platform_phase',query=dict(id='carrier',window=[phase,phase+.02]),timeout=900),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(1160,6)]
  reward(c,1160,420);finish(c,1160,420,p);c['trace_all']=True;c['max_frames']=1400;out.append(c)
 for phase in [.37,.44]:
  c=base('lift-'+str(phase));c['family']='elevator-headroom';c['platforms']+=[[420,65,230,100]];c['moving_platforms']=[platform('carrier',[310,448],[310,50],2.2,1.2)]
  p=board()+[dyn('wait','platform_phase',query=dict(id='carrier',window=[phase,phase+.02]),timeout=900),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=10),settle(530,6)]
  reward(c,530,47);finish(c,530,47,p);c['trace_all']=True;c['max_frames']=1500;out.append(c)
 for phase in [.38,.48]:
  c=base('transfer-'+str(phase));c['family']='carrier-rendezvous';c['platforms']+=[[1310,438,230,100]];c['moving_platforms']=[platform('carrier',[300,448],[650,448],2.,1.2),platform('other',[920,448],[1100,448],2.,1.2)]
  p=board()+[dyn('wait','platform_phase',query=dict(id='carrier',window=[phase,phase+.02]),timeout=900),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),dyn('wait','on_platform',query=dict(id='other'),timeout=180),cmd('axis',value=0),cmd('wait',after=20),cmd('axis',value=1),cmd('jump'),cmd('jump_release',after=12),cmd('shoot',after=6,direction=[-.97,.243]),settle(1420,6)]
  reward(c,1420,420);finish(c,1420,420,p);c['trace_all']=True;c['max_frames']=1700;out.append(c)
 for phase in [.26,.51,.76]:
  c=base('pursuit-'+str(phase));c['family']='saw-pursuit';c['platforms']=[[-160,438,1400,100],[240,250,640,125]];c['saws']=[dict(source_id='pursuer',origin=[560,414],travel=[300,0],radius=24,period=6.,initial_phase=0.,damage=1,contact_interval=.7)]
  p=[cmd('axis',value=1),wait_x(180),cmd('axis',value=0),dyn('wait','saw_phase',query=dict(id='pursuer',window=[phase,phase+.02]),timeout=900),cmd('axis',value=1),settle(1030,after=6)]
  reward(c,1030,420);finish(c,1030,420,p);c['trace_all']=True;c['max_frames']=1300;out.append(c)
 return out
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-machinery-probe-v1';e=WorkshopEngine(out,extra_sources=[Path(__file__)])
 rows=[]
 for c,r,ev in e.run(candidates(),'geometry-probe'):
  frames=r.get('frames',[]);s={f.get('support_id')for f in frames};row=dict(id=c['id'],ok=r.get('ok'),reason=r.get('reason'),error=r.get('plan_error'),supports=list(s),hp=r.get('hp'),last=frames[-1]if frames else None,shots=r.get('shots'),evidence=ev);rows.append(row);print(json.dumps({k:v for k,v in row.items()if k!='last'}),flush=True)
 (out/'summary.json').write_text(json.dumps(rows,indent=2))
