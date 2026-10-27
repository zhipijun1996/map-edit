"""Late falling displacement and horizontal-door shielding exploration."""
from pathlib import Path
import json
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import base,cmd,settle,reward,finish,wait_x
HERE=Path(__file__).parent

def cases():
 out=[]
 for delay in [14,17,20,23]:
  c=base('ew-late-displace-'+str(delay));c['family']='enemy-displace-landing';c['production_recipe']='displace-landing'
  c['platforms']=[[-160,238,350,100],[-160,438,900,100]];c['spawn']=[170,220];c['entry_port']=[170,220]
  c['enemies']=[dict(id='occupant',definition='plains_sentry',position=[225,422],initial_idle_cooldown=.6)]
  reward(c,208,420,12)
  finish(c,208,420,[cmd('axis',value=1),wait_x(205),cmd('axis',value=0),cmd('shoot',delay,aim_cell=dict(kind='enemy',id='occupant')),settle(208,24)])
  c['goal']=[202,416,12,8];c['max_frames']=220;c['trace_all']=False;out.append(c)
 for duration in [.65,.8,.95,1.1]:
  c=base('ew-floor-shield-'+str(duration));c['family']='enemy-closing-shield';c['production_recipe']='closing-shield'
  c['platforms']=[[-160,438,480,100],[460,438,400,100],[300,628,190,100],[290,280,30,100]]
  c['spawn']=[270,420];c['entry_port']=[270,420]
  c['enemies']=[dict(id='pursuer',definition='plains_sentry',position=[420,402],initial_idle_cooldown=.6)]
  c['latches']=[dict(id='shield',bell=[280,410],gate=[320,438,140,20],open_seconds=duration)]
  reward(c,380,610,12)
  finish(c,380,610,[cmd('shoot',aim_cell=dict(kind='bell',id='shield')),settle(380,15),cmd('wait',110)])
  c['max_frames']=300;c['trace_all']=False;out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v4',extra_sources=[Path(__file__),HERE/'runner_v1.gd'],runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e))
  print(c['id'],r['ok'],r['reason'],r.get('shots'),r.get('hp'),r.get('plains',{}).get('events'),r.get('enemy_world'),[(f['frame'],round(f['x']),round(f['y']))for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
