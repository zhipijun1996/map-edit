import argparse,json
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['clean','noise','counters'],default='clean');p.add_argument('--interface',type=int,default=0);p.add_argument('--controls',type=int,nargs='+',default=[0,1,2,3]);a=p.parse_args()
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT)
 source=[rules.materialize(a.interface,i)for i in a.controls]
 if a.mode=='clean':cs=source
 elif a.mode=='noise':cs=[instantiate(c,261031037,lev,i)for c in source for lev in ['mild','moderate']for i in range(6)]
 else:cs=[v for c in source for v in rules.alternatives(c)]
 rows=[]
 for c,r,ev in e.run(cs,a.mode):
  q=rules.purpose(c,r);fs=r.get('frames',[]);last=fs[-1]if fs else{};rows.append(dict(case=c,result=r,evidence=ev,purpose=q))
  print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],last={k:last.get(k)for k in ['frame','x','y','grounded','support_id']},swap=q['causal']['actual_swap'],landing=q['causal']['first_landing'],coins=r.get('workshop',{}).get('coins'))),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows)))
if __name__=='__main__':main()
