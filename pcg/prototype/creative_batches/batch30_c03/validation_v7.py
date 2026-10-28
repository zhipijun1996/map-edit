import argparse,json
from pathlib import Path
from . import api_v1 as api
from . import validation_v6 as prior
from .validation_v5 import dead_check
from .repair_v4 import compact
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
HERE=Path(__file__).parent
def dead_fixture():
 c=prior.dead_fixture(0);c['id']+='-close-from140'
 for q in c['control_plan']:
  d=q.get('trigger',{}).get('dynamic',{})
  if d.get('kind')=='actor_x'and d.get('value')==90:d['value']=140
 c['validation_fixture']['closing_shooting_position']=140
 return c
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'verification-protocol-v5.json',HERE/'validation_v6.py',HERE/'validation_v5.py',HERE/'repair_v4.py',Path(api.__file__),*api.SOURCE_DEPENDENCIES],runner_script=api.RUNNER_SCRIPT);rows=[];good=False;c=dead_fixture()
 for case,r,e in engine.run([c],'real-clear-close140-clean'):
  q=dead_check(case,r);good=q['ok'];rows.append(compact(case,r,e,q));print(json.dumps(dict(id=case['id'],ok=q['ok'],why=q['reasons'],hp=r.get('hp'),enemy=r.get('plains',{}).get('enemies'),shots=r.get('shots'))),flush=True)
 if good:
  for case,r,e in engine.run([instantiate(c,261031101,'mild',k)for k in range(2)],'real-clear-close140-mild'):
   q=dead_check(case,r);rows.append(compact(case,r,e,q));print(json.dumps(dict(id=case['id'],ok=q['ok'],why=q['reasons'])),flush=True)
 write(engine.out/'validation-results.json',rows);print(json.dumps(dict(actual_cases=engine.sim.cases,total=217+engine.sim.cases)),flush=True)
if __name__=='__main__':main()
