"""Last registered geometry repair, strict first-support observation."""
import argparse,json
from pathlib import Path
from . import api_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','noise','counters'],required=True);p.add_argument('--control',type=int,default=0);a=p.parse_args()
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT)
 if a.stage=='clean':cases=[rules.materialize(i,k)for i in [0,1]for k in [0,1]]
 elif a.stage=='noise':cases=[instantiate(rules.materialize(i,a.control),261029019,l,t)for i in [0,1]for l in ['mild','moderate']for t in range(6)]
 else:
  cases=[]
  for i in [0,1]:
   alts=rules.alternatives(rules.materialize(i,a.control))
   # At least18 per exact geometry, all12 actual ride-launch attempts plus
   # ordinary/direct recoil, missing shots, extra air shot, roof/floor paths.
   cases+=alts[:4]+alts[12:16]+alts[18:24]+alts[30:]
 rows=[]
 for c,r,b in e.run(cases,'strict-first-support-'+a.stage):
  check=rules.purpose(c,r);same=bool(r.get('ok'))and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])and r.get('workshop',{}).get('coins',0)>=12
  rows.append(dict(case=c,result=r,check=check,same_external_outcome=same,evidence=b));print(json.dumps(dict(id=c['id'],check=check,external=same)),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['check']['ok']for v in rows),rows=rows))
if __name__=='__main__':main()
