"""Bounded preregistered screening; no holdout or store mutation."""
import argparse,json
from pathlib import Path
from . import api_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--counters',action='store_true');a=p.parse_args()
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT)
 cases=([v for interface in [0,1]for v in rules.alternatives(rules.materialize(interface,0))]if a.counters else[instantiate(rules.materialize(i,k),261029019,level,t)for i in [0,1]for k in [0,1]for level in ['clean','mild','moderate']for t in range(1 if level=='clean'else 6)])
 rows=[]
 for c,r,b in e.run(cases,'adapted-counters'if a.counters else'two-receiver-equal-screen'):
  check=rules.purpose(c,r);same=bool(r.get('ok'))and r.get('hp')==5 and not r.get('returns')and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])and r.get('workshop',{}).get('coins',0)>=12
  rows.append(dict(case=c,result=r,check=check,same_external_outcome=same,evidence=b));print(json.dumps(dict(id=c['id'],check=check,external=same,last=[r['frames'][-1].get(k)for k in ['x','y','support_id']]if r.get('frames')else[])),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['check']['ok']for v in rows),rows=rows))
if __name__=='__main__':main()
