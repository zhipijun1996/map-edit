import argparse,json
from pathlib import Path
from . import rules_v3 as rules
from .probe_v1 import report
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--level',choices=['clean','mild','moderate'],default='mild');p.add_argument('--trials',type=int,default=6);a=p.parse_args();e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),HERE/'probe_v1.py']+rules.SOURCE_DEPENDENCIES);rows=[]
 bases=[c for i in [0,1]for c in rules.layouts(rules.RECIPES[0],i)];cs=[instantiate(c,261026930,a.level,j)for c in bases for j in range(1 if a.level=='clean'else a.trials)]
 for c,r,ev in e.run(cs,'bounded-'+a.level+'-screen'):
  row=report(c,r,ev);row['purpose']=rules.purpose(c,r);rows.append(row);print(json.dumps(dict(id=c['id'],ok=row['purpose']['ok'],reason=r.get('reason'),purpose=row['purpose'],evidence=ev)),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),rows=[dict(id=x['case']['id'],purpose=x['purpose'],evidence=x['evidence'])for x in rows]))
