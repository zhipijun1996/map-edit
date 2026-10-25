import sys,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'prototype/composable'))
from synthesis import gated
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle,reward,finish
OWN=Path(__file__);AD=OWN.with_name('runner-capabilities-v1.gd');OUT=ROOT/'results/workshop-creative-jump-wall-wallslide-probes-v1';eng=WorkshopEngine(OUT,extra_sources=[OWN,AD],runner_script=AD)
cs=[]
for delay in [190,205,220,235]:
 c=base('wallslide-'+str(delay));c['family']='wall-slide-launch-window';c['capabilities']=['move','wall_climb'];c['platforms']=[[90,18,50,60],[195,-80,32,1000],[40,-150,20,250],[40,300,20,650],[-180,318,200,30]];c['wall_platform_indices']=[1];c['one_way_platform_indices']=[];c['spawn']=[110,0];c['entry_port']=[110,0];c['world_bounds']=[-1200,-1200,4000,4000];c['thorns']=[dict(surface_id='upper-mouth',platform_index=2,face='right',start_offset=0,length=250,depth=8),dict(surface_id='lower-mouth',platform_index=3,face='right',start_offset=0,length=650,depth=8)];reward(c,-90,300)
 finish(c,-90,300,[cmd('axis',value=1),gated('wait','wall_attach',min_after=3,timeout=120),cmd('wait',delay),gated('jump','wall_attach',min_after=0),gated('axis','wall_kick',min_after=1,timeout=12,value=-1),cmd('jump_release',8),settle(-90,3)]);c['max_frames']=650;c['trace_all']=True;cs.append(c)
for c,r,e in eng.run(cs,'wallslide'):
 (OUT/(c['id']+'.json')).write_text(json.dumps(dict(case=c,result=r,evidence=e)))
 fs=r.get('frames',[]);print(c['id'],r['reason'],r.get('plan_error'),r.get('workshop',{}).get('coins'),'events',[(f['frame'],round(f['x']),round(f['y']),f['traversal_state'],[q.get('state',q['type'])for q in f['accepted']])for f in fs if f['accepted']],'cross',[(f['frame'],round(f['x']),round(f['y']))for f in fs if 20<f['x']<90 and f['frame']>100][::3],flush=True)
