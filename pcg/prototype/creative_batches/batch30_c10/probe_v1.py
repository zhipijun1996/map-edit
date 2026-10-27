import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--route',choices=['main','recovery'],default='main');p.add_argument('--controls',type=int,nargs='+',default=[0,1,2,3]);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run([rules.materialize(0,a.route,i)for i in a.controls],'clean'):
  q=rules.purpose(c,r);last=r.get('frames',[{}])[-1];row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','hp','shots','jumps']},last={k:last.get(k)for k in ['frame','x','y','support_id']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(x['purpose']['ok']for x in rows)))
if __name__=='__main__':main()
