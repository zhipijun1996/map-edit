import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from . import rules_v1 as rules
from .alternatives_v1 import alternatives
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),HERE/'alternatives_v1.py',Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 cs=[instantiate(rules.candidate(0,0),261031101,'mild',i)for i in range(6)]+alternatives(rules.candidate(0,0))
 for c,r,e in engine.run(cs,'mild-and-cheap'):
  q=rules.purpose(c,r);same=bool(r.get('ok'))and r.get('hp')==5 and r.get('workshop',{}).get('coins',0)>=12 and not any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])and not r.get('returns')
  rows.append(dict(case=c,result=r,purpose=q,evidence=e,same_external_outcome=same,invalidates_design='-counter-'in c['id']and same and not q['ok']));print(json.dumps(dict(id=c['id'],ok=q['ok'],same=same,why=q['reasons'],min_y=min((f['y']for f in r.get('frames',[])),default=None))),flush=True)
 write(engine.out/'screen-results.json',rows)
if __name__=='__main__':main()
