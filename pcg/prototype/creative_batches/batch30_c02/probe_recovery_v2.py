import argparse,json
from pathlib import Path
from . import recovery_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['clean','noise'],default='clean');a=p.parse_args()
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.rules.RUNNER_SCRIPT)
 cs=[rules.materialize(i,c)for i in range(2)for c in range(2)]if a.mode=='clean'else[instantiate(rules.materialize(i,0),261031037,lev,n)for i in range(2)for lev in ['mild','moderate']for n in range(6)]
 rows=[]
 for c,r,ev in e.run(cs,a.mode):
  q=rules.purpose(c,r);last=r.get('frames',[{}])[-1];rows.append(dict(case=c,result=r,evidence=ev,purpose=q))
  print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],last={k:last.get(k)for k in ['frame','x','y','support_id']},recovered=q['causal']['original_A_returned_frames'],swaps=q['causal']['all_swaps'])),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows)))
if __name__=='__main__':main()
