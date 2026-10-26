"""Actual enemy firing opens a short gate, then native projectile avoidance."""
from pathlib import Path
import json
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import base,cmd,settle,reward,finish,wait_x
HERE=Path(__file__).parent

def state():return dict(op='wait',trigger=dict(state='grounded',enemy_state=dict(id='relay-sentry',state='attack'),timeout=180))
def cases():
 out=[]
 for delay in [0,3,6,9]:
  c=base('ew-attack-relay-'+str(delay));c['family']='enemy-attack-relay';c['production_recipe']='attack-relay'
  c['platforms']=[[-160,438,900,100],[210,346,60,50],[300,330,440,66]]
  c['enemies']=[dict(id='relay-sentry',definition='plains_sentry',position=[225,330],initial_idle_cooldown=.6)]
  c['latches']=[dict(id='attack-gate',bell=[270,310],gate=[300,396,24,42],open_seconds=.8,attack_relay=dict(enemy_id='relay-sentry',native_state='attack'))]
  reward(c,420,420,12)
  finish(c,420,420,[cmd('axis',value=0),state(),cmd('axis',delay,value=1),settle(420)])
  c['max_frames']=360;c['trace_all']=False;out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-probe-v8',extra_sources=[Path(__file__),HERE/'runner_v1.gd',HERE/'attack_relay_v1.gd',HERE/'attack_runner_v1.gd'],runner_script=HERE/'attack_runner_v1.gd');rows=[]
 for c,r,e in engine.run(cases(),'probe'):
  rows.append(dict(case=c,result=r,evidence=e));print(c['id'],r['ok'],r['reason'],r.get('hp'),r.get('plains',{}).get('events'),r.get('enemy_world'),[(f['frame'],round(f['x']),round(f['y']))for f in r.get('frames',[])[::20]],flush=True)
 (engine.out/'rows.json').write_text(json.dumps(rows))
