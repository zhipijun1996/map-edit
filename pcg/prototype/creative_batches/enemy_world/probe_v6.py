"""Authored stationary native charger + original occupancy Cell probe."""
from pathlib import Path
import json
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import base,cmd,settle,reward,finish,wait_x
HERE=Path(__file__).parent
SOURCES=[HERE/'occupancy_runner_v1.gd',HERE/'guard_charger_v1.tres']+list((HERE.parent/'occupancy').glob('*v1.gd'))+[HERE.parent/'occupancy/main_v1.tscn']

def state(id,value):return dict(op='wait',trigger=dict(state='grounded',enemy_state=dict(id=id,state=value),timeout=240))
def cases():
 out=[]
 for delay in [0,4,8,12]:
  c=base('ew-lure-guard-'+str(delay));c['family']='enemy-lure-sensor';c['production_recipe']='lure-sensor'
  c['platforms']=[[-160,300,314,50],[-160,438,900,100],[270,330,500,66]];c['spawn']=[140,282];c['entry_port']=[140,282]
  c['enemies']=[dict(id='guard',definition='plains_charger',variant_definition='enemy-world/guard-charger-v1',position=[225,422],initial_idle_cooldown=.6)]
  c['latches']=[dict(id='enemy-sensor',bell=[108,400],gate=[270,396,24,42],open_seconds=.05,occupancy=dict(mode='enemy_alive',rect=[108,405,24,33]))]
  reward(c,420,420,12)
  finish(c,420,420,[cmd('axis',value=0),state('guard','attack'),cmd('axis',delay,value=1),wait_x(235),settle(420)])
  c['max_frames']=400;c['trace_all']=False;out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v6',extra_sources=[Path(__file__)]+SOURCES,runner_script=HERE/'occupancy_runner_v1.gd');rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e));print(c['id'],r['ok'],r['reason'],r.get('hp'),r.get('plains',{}).get('events'),[(f['frame'],round(f['x']),round(f['y']),f['plains']['enemies'])for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
