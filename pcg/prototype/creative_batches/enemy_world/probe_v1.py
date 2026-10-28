"""Frozen exploratory original-Godot probes; proposals only, no certification."""
from pathlib import Path
import json,copy
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import base,cmd,settle,reward,finish,wait_x

def cases():
 out=[]
 for spacing in [12,18,24,30]:
  c=base('ew-brace-probe-'+str(spacing));c['family']='ew-brace-clearance'
  c['platforms']=[[-160,438,900,120],[-160,330,900,60],[-20,390,30,48],[310,390,30,48]]
  c['spawn']=[30,420];c['entry_port']=[30,420]
  c['enemies']=[dict(id='roadblock',definition='plains_sentry',position=[220,422],initial_idle_cooldown=.6)]
  c['production_recipe']='brace-clearance';reward(c,440,420,12)
  plan=[cmd('axis',value=0)]+[cmd('shoot',spacing if i else 0,aim_cell=dict(kind='enemy',id='roadblock'))for i in range(3)]+[settle(440,40)]
  finish(c,440,420,plan);c['max_frames']=220;c['trace_all']=True;out.append(c)
 for spacing in [12,18,24,30]:
  c=base('ew-absorber-probe-'+str(spacing));c['family']='ew-absorber-bell'
  c['platforms']=[[-160,438,1000,100],[-160,330,1000,60],[-20,390,30,48]]
  c['spawn']=[30,420];c['entry_port']=[30,420]
  c['enemies']=[dict(id='absorber',definition='plains_sentry',position=[240,422],initial_idle_cooldown=.6)]
  c['latches']=[dict(id='far-bell',bell=[390,416],gate=[490,390,24,48],open_seconds=0)]
  c['production_recipe']='absorber-bell';reward(c,650,420,14)
  plan=[cmd('axis',value=0)]+[cmd('shoot',spacing if i else 0,aim_cell=dict(kind='bell',id='far-bell'))for i in range(4)]+[settle(650,40)]
  finish(c,650,420,plan);c['max_frames']=280;c['trace_all']=True;out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v1',extra_sources=[Path(__file__)])
 rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e))
  print(c['id'],r['ok'],r['reason'],r.get('shots'),r.get('hp'),r.get('plains',{}).get('events'),[(f['frame'],round(f['x']),round(f['y']))for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
