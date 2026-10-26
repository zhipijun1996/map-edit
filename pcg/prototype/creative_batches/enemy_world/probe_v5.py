"""Native charger body relocation and late-shot variants."""
from pathlib import Path
import json
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import base,cmd,settle,reward,finish,wait_x
HERE=Path(__file__).parent

def state(id,value):return dict(op='wait',trigger=dict(state='grounded',enemy_state=dict(id=id,state=value),timeout=180))
def cases():
 out=[]
 for departure in [0,4,8,12]:
  c=base('ew-bait-charger-'+str(departure));c['family']='enemy-bait-clearance';c['production_recipe']='bait-clearance'
  c['platforms']=[[-160,300,350,50],[-160,438,900,100],[260,330,500,66]];c['spawn']=[130,282];c['entry_port']=[130,282]
  c['enemies']=[dict(id='charger',definition='plains_charger',position=[225,422],initial_idle_cooldown=.6)]
  reward(c,420,420,12)
  finish(c,420,420,[cmd('axis',value=0),state('charger','attack'),cmd('axis',departure,value=1),wait_x(235),settle(420)])
  c['max_frames']=300;c['trace_all']=False;out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v5',extra_sources=[Path(__file__),HERE/'runner_v1.gd',HERE/'runner_v2.gd'],runner_script=HERE/'runner_v2.gd');rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e))
  print(c['id'],r['ok'],r['reason'],r.get('shots'),r.get('hp'),r.get('plains',{}).get('events'),[(f['frame'],round(f['x']),round(f['y']),f['plains']['enemies'])for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
