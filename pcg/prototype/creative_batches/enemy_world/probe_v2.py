"""Second isolated world relation probes, frozen exploratory source."""
from pathlib import Path
import json
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import base,cmd,settle,reward,finish,wait_x
HERE=Path(__file__).parent

def cases():
 out=[]
 # A live enemy occupies the precise lower reward landing. One hit moves it.
 for x in [196,200,204,208]:
  c=base('ew-displace-probe-'+str(x));c['family']='enemy-displace-landing';c['production_recipe']='displace-landing'
  c['platforms']=[[-160,238,350,100],[-160,438,900,100]];c['spawn']=[170,220];c['entry_port']=[170,220]
  c['enemies']=[dict(id='occupant',definition='plains_sentry',position=[225,422],initial_idle_cooldown=.6)]
  reward(c,x,420,12)
  plan=[cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='enemy',id='occupant')),settle(x,24)]
  finish(c,x,420,plan);c['goal']=[x-3,416,6,8];c['max_frames']=220;c['trace_all']=True;out.append(c)
 # Open a shield into a short enemy firing line; timed original gate closes.
 for duration in [.35,.5,.65,.8]:
  c=base('ew-shield-probe-'+str(duration));c['family']='enemy-closing-shield';c['production_recipe']='closing-shield'
  c['platforms']=[[-160,438,900,100],[-160,330,900,66]];c['spawn']=[80,420];c['entry_port']=[80,420]
  c['enemies']=[dict(id='pursuer',definition='plains_sentry',position=[10,422],initial_idle_cooldown=.6)]
  c['latches']=[dict(id='shield',bell=[110,416],gate=[160,396,20,42],open_seconds=duration)]
  reward(c,220,420,12)
  plan=[cmd('shoot',aim_cell=dict(kind='bell',id='shield')),settle(220,15),cmd('wait',150)]
  finish(c,220,420,plan);c['max_frames']=300;c['trace_all']=True;out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v2',extra_sources=[Path(__file__),HERE/'runner_v1.gd'],runner_script=HERE/'runner_v1.gd')
 rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e))
  print(c['id'],r['ok'],r['reason'],r.get('shots'),r.get('hp'),r.get('plains',{}).get('events'),r.get('enemy_world'),[(f['frame'],round(f['x']),round(f['y']))for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
