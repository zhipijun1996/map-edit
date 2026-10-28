import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__)]+rules.SOURCE_DEPENDENCIES,runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,b in e.run([rules.candidate(0,i)for i in range(4)],'core-catch-probe'):
  q=rules.purpose(c,r);fs=r.get('frames',[]);row=dict(case=c,result=r,check=q,evidence=b);rows.append(row);print(json.dumps(dict(id=c['id'],purpose=q,last=({k:fs[-1].get(k)for k in ['frame','x','y','support_id']}if fs else{}),fired=r.get('fired_commands'))),flush=True)
 write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(x['check']['ok']for x in rows),rows=rows))
