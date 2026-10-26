import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'prototype/composable'))
from synthesis import gated
from pcg.prototype.workshop.engine import WorkshopEngine
from pcg.prototype.workshop.measure import base
from pcg.prototype.workshop.rules import cmd,settle,reward,finish
OWN=Path(__file__);AD=OWN.with_name('runner-capabilities-v1.gd');OUT=ROOT/'results/workshop-creative-jump-wall-rebound-probes-v2';eng=WorkshopEngine(OUT,extra_sources=[OWN,AD],runner_script=AD)
cs=[]
for wall in [195,225]:
 for by in [480,510]:
  c=base(f'rebound-{wall}-{by}');c['family']='bell-wall-rebound';c['capabilities']=['move','shot_recoil','wall_climb'];c['platforms']=[[68,438,24,60],[wall,120,32,700],[-140,298,200,24]];c['wall_platform_indices']=[1];c['one_way_platform_indices']=[2];c['latches']=[dict(id='reverse-bell',bell=[0,by],gate=[70,80,20,250],open_seconds=1.6)];reward(c,-40,280)
  finish(c,-40,280,[cmd('axis',value=0),cmd('shoot',0,aim_cell=dict(kind='bell',id='reverse-bell')),cmd('axis',1,value=1),gated('wait','wall_attach',min_after=3,timeout=120),gated('jump','wall_attach',min_after=3),gated('axis','wall_kick',min_after=1,timeout=12,value=-1),cmd('jump_release',8),settle(-40,5)]);c['max_frames']=360;c['trace_all']=True;cs.append(c)
for c,r,e in eng.run(cs,'rebound'):
 (OUT/(c['id']+'.json')).write_text(json.dumps(dict(case=c,result=r,evidence=e)))
 print(c['id'],r['reason'],r.get('plan_error'),r.get('workshop',{}).get('coins'),r.get('plains',{}).get('events'),[(f['frame'],round(f['x']),round(f['y']),f['traversal_state'],f['shot_charges'],[a['type']for a in f['accepted']])for f in r.get('frames',[])if f['accepted']],flush=True)
