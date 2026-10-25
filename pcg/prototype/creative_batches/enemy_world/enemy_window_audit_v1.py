"""Postselection explanatory native audits, no selection or difficulty changes."""
from pathlib import Path
import copy,json
from pcg.prototype.creative_batches.enemy_world.production_v7 import compiler,sources,HERE
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import cmd,settle,wait_x

def cases(recipe):
 c=compiler(dict(recipe=recipe))['cases'][0];out=[]
 for delay in [0,20,40,60,90,120]:
  v=copy.deepcopy(c);v['id']+='-counter-window-'+str(delay);v['counterexample_kind']='actual_enemy_window_pause'
  if recipe=='lure-sensor':v['control_plan']=c['control_plan'][:3]+[wait_x(235),cmd('axis',value=0),cmd('wait',delay),settle(420)]
  else:v['control_plan']=c['control_plan'][:2]+[cmd('wait',delay),settle(420)]
  out.append(v)
 return out
if __name__=='__main__':
 for recipe,runner in [('lure-sensor','occupancy_runner_v2.gd'),('attack-relay','attack_runner_v1.gd')]:
  engine=WorkshopEngine(ROOT/('results/workshop-creative-enemy-world-window-'+recipe+'-audit-v1'),extra_sources=sources()+[Path(__file__)],runner_script=HERE/runner);rows=[]
  for c,r,e in engine.run(cases(recipe),'window-audit'):
   row=dict(id=c['id'],safe_stable=r['ok'],hp=r.get('hp'),reason=r['reason'],coins=r.get('workshop',{}).get('coins'),events=r.get('plains',{}).get('events'),enemy_world=r.get('enemy_world'),evidence=e);rows.append(row);print(json.dumps(row),flush=True)
  (engine.out/'audit.json').write_text(json.dumps(rows,indent=2))
