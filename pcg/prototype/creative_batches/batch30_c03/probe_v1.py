import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from . import rules_v1 as rules
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
 engine=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,e in engine.run([rules.candidate(0,k)for k in range(4)],'air-core'):
  q=rules.purpose(c,r);rows.append(dict(case=c,result=r,purpose=q,evidence=e));print(json.dumps(dict(id=c['id'],purpose=q,reason=r.get('reason'),last={k:r.get('frames',[{}])[-1].get(k)for k in ['x','y','support_id']},min_y=min((f['y']for f in r.get('frames',[])),default=None),enemies=r.get('plains',{}).get('enemies'))),flush=True)
 write(engine.out/'probe-results.json',rows)
if __name__=='__main__':main()
