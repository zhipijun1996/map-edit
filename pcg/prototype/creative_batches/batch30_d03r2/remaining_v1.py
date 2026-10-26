import json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.creative_batches.batch30_d03.probe_v1 import report
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent
if __name__=='__main__':
 e=WorkshopEngine(ROOT/'results/workshop-batch30-d03r2-remainder-v1',extra_sources=[Path(__file__),Path(rules.__file__),ROOT/'prototype/creative_batches/batch30_d03/probe_v1.py',HERE/'remaining-protocol-v1.json']+rules.SOURCE_DEPENDENCIES);rows=[];cs=[]
 for i in (0,1):
  bases=[c for c in rules.layouts(rules.RECIPES[0],i)if c['route_spec']['id']in ['east-staged','main']]
  if i==0:cs.extend(instantiate(c,261027001,'moderate',j)for c in bases for j in range(6,12))
  cs.extend(instantiate(c,261027001,'mild',j)for c in bases for j in range(2))
 cs+=rules.depleted_comparisons(rules.RECIPES[0],0)
 for c,r,ev in e.run(cs,'bounded-r2-v1-remainder'):
  row=report(c,r,ev);row['purpose']=rules.purpose(c,r);rows.append(row);print(json.dumps(dict(id=c['id'],ok=row['purpose']['ok'],reason=r.get('reason'),purpose=row['purpose'],evidence=ev)),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(v['purpose']['ok']for v in rows),rows=[dict(id=x['case']['id'],purpose=x['purpose'],safe_stable=x['result'].get('ok'),evidence=x['evidence'])for x in rows]))
