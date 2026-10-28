"""Six repaired reachable-ground controllers, before root's full counter pass."""
import json
from pathlib import Path
from . import api_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def main():
 e=WorkshopEngine(ROOT/'results/workshop-batch30-c02-reachable-counters-v1',extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT)
 cs=[]
 for i in range(2):
  c=rules.layouts(rules.RECIPES[0],i)[0];needle='reachable-ground-middle-open-and-climb-'+str(c['latches'][0]['paired_gate'][0]-40)+'-'
  cs += [v for v in rules.alternatives(c)if v['counterexample_kind'].startswith(needle)]
 rows=[]
 for c,r,ev in e.run(cs,'reachable-ground-counter'):
  q=rules.purpose(c,r);rows.append(dict(case=c,result=r,evidence=ev,purpose=q));print(json.dumps(dict(id=c['id'],stable=r.get('ok'),coins=r.get('workshop',{}).get('coins'),purpose=q)),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,same_goal_refutations=sum(x['result'].get('ok',False)and x['result'].get('workshop',{}).get('coins',0)>=12 and not x['purpose']['ok']for x in rows)))
if __name__=='__main__':main()
