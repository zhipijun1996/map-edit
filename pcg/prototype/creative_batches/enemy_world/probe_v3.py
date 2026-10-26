"""Terrain and phase revision probes; original scripts unmodified."""
from pathlib import Path
import json
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import base,cmd,settle,reward,finish,wait_x
HERE=Path(__file__).parent

def cases():
 out=[]
 for spacing in [18,21,24,27]:
  c=base('ew-near-clear-'+str(spacing));c['family']='enemy-clear-sightline';c['production_recipe']='clear-sightline'
  c['platforms']=[[-160,438,1000,100],[-160,330,1000,66],[40,396,30,42]]
  c['spawn']=[90,420];c['entry_port']=[90,420]
  c['enemies']=[dict(id='absorber',definition='plains_sentry',position=[170,422],initial_idle_cooldown=0)]
  c['latches']=[dict(id='far-bell',bell=[230,416],gate=[300,396,24,42],open_seconds=0)]
  reward(c,450,420,14)
  finish(c,450,420,[cmd('axis',value=0)]+[cmd('shoot',spacing if i else 0,direction=[1,0])for i in range(3)]+[cmd('shoot',spacing,aim_cell=dict(kind='bell',id='far-bell')),settle(450,30)])
  c['max_frames']=320;c['trace_all']=True;out.append(c)
 for x in [204,208,212,216]:
  c=base('ew-displace-edge-'+str(x));c['family']='enemy-displace-landing';c['production_recipe']='displace-landing'
  c['platforms']=[[-160,238,350,100],[-160,438,900,100]];c['spawn']=[170,220];c['entry_port']=[170,220]
  c['enemies']=[dict(id='occupant',definition='plains_sentry',position=[225,422],initial_idle_cooldown=.6)]
  reward(c,x,420,12)
  finish(c,x,420,[cmd('axis',value=1),wait_x(205),cmd('axis',value=0),cmd('shoot',aim_cell=dict(kind='enemy',id='occupant')),settle(x,24)])
  c['goal']=[x-4,416,8,8];c['max_frames']=240;c['trace_all']=True;out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v3',extra_sources=[Path(__file__),HERE/'runner_v1.gd'],runner_script=HERE/'runner_v1.gd');rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e))
  print(c['id'],r['ok'],r['reason'],r.get('shots'),r.get('hp'),r.get('plains',{}).get('events'),r.get('enemy_world'),[(f['frame'],round(f['x']),round(f['y']))for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
