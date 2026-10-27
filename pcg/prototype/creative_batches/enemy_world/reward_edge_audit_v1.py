"""Supplemental audit: actual reward and alternative safe positions, no goal-center assumption.
These audit cases expand goal to the unchanged actual reward region, and are NOT
published-module validation of a changed target. All physical geometry stays exact.
"""
from pathlib import Path
import copy,json
from pcg.prototype.creative_batches.enemy_world.production_v3 import compiler as old_compile
from pcg.prototype.creative_batches.enemy_world.production_v6 import compiler as new_compile
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import cmd,settle,wait_x
HERE=Path(__file__).parent

def cases():
 out=[]
 for label,fn in [('old-broad-floor-v3',old_compile),('physical-thorns-v6',new_compile)]:
  base=fn(dict(recipe='displace-landing'))['cases'][0]
  for delay in [12,14,16,18]:
   for x in [185,190,195,200]:
    c=copy.deepcopy(base);c['id']+='-counter-reward-edge-'+str(delay)+'-'+str(x)
    c['counterexample_kind']='actual-reward-safe-left-'+label;c['goal']=c['reward_sites'][0]['region'][:]
    c['control_plan']=[cmd('axis',value=1),wait_x(205),cmd('axis',value=0),cmd('axis',delay,value=-1),settle(x,4)]
    out.append(c)
 return out
if __name__=='__main__':
 engine=WorkshopEngine(ROOT/'results/workshop-creative-enemy-world-reward-edge-audit-v1',extra_sources=[Path(__file__)]+[HERE/('production_v'+str(v)+'.py')for v in[3,4,5,6]]+[HERE/'probe_v4.py']);rows=[]
 for c,r,e in engine.run(cases(),'edge-audit'):
  rows.append(dict(id=c['id'],kind=c['counterexample_kind'],safe_stable=r['ok'],coins=r.get('workshop',{}).get('coins'),hp=r.get('hp'),reason=r['reason'],evidence=e))
  print(c['id'],r['ok'],r.get('workshop',{}).get('coins'),r['reason'],flush=True)
 (engine.out/'audit.json').write_text(json.dumps(rows,indent=2))
