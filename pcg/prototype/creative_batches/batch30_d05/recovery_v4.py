"""Same v3 geometry, correct long lower-floor walk timeout."""
import argparse,json
from pathlib import Path
from . import recovery_v3 as previous
from . import api_v2 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def fixture(i):
 c=previous.fixture(i);c['id']=c['id'].replace('recovery-c0','recovery-c1')
 for q in c['control_plan']:
  if q.get('trigger',{}).get('dynamic',{}).get('value')==-620:q['trigger']['timeout']=650
 return c
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--noise',action='store_true');a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(previous.__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT)
 cs=[instantiate(fixture(i),261029019,l,t)for i in [0,1]for l in ['mild','moderate']for t in range(6)]if a.noise else[fixture(i)for i in [0,1]];rows=[]
 for c,r,b in e.run(cs,'missed-bell-real-recovery'):
  q=previous.purpose(c,r);rows.append(dict(case=c,result=r,check=q,evidence=b));print(json.dumps(dict(id=c['id'],check=q,last=[r['frames'][-1].get(k)for k in ['x','y','support_id']])),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['check']['ok']for v in rows),rows=rows))
if __name__=='__main__':main()
