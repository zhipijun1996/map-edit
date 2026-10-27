import argparse,json
from pathlib import Path
from . import api_v1 as api
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();c=api.layouts(api.RECIPES[0],0)[1];e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(api.__file__)]+api.SOURCE_DEPENDENCIES,runner_script=api.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(api.alternatives(c),'counters'):
  q=api.purpose(c,r);row=dict(id=c['id'],counter_kind=c['counterexample_kind'],purpose=q,result={k:r.get(k)for k in ['ok','reason','hp','shots','jumps']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows)))
if __name__=='__main__':main()
