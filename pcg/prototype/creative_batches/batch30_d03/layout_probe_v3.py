import argparse,json
from pathlib import Path
from . import rules_v3 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from .probe_v1 import report
HERE=Path(__file__).parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',default='workshop-batch30-d03-layout-probe-v3');p.add_argument('--interface',type=int,default=0);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),HERE/'probe_v1.py']+rules.SOURCE_DEPENDENCIES);rows=[]
 for c,r,ev in e.run(rules.layouts(rules.RECIPES[0],a.interface),'finite-route-layout'):
  row=report(c,r,ev);row['purpose']=rules.purpose(c,r);rows.append(row);print(json.dumps(dict(id=c['id'],summary=row['summary'],purpose=row['purpose'])),flush=True)
 write(e.out/'probe-results.json',rows)
