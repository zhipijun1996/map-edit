"""Twelve omitted-shot falsifiers plus two final exact canonical prototypes."""
import json
from pathlib import Path
from . import rules_v5 as rules
from .probe_v1 import report
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.factory.core.quality import digest,module_hash
HERE=Path(__file__).parent
if __name__=='__main__':
 e=WorkshopEngine(ROOT/'results/workshop-batch30-d03-counter-v5',extra_sources=[Path(__file__),Path(rules.__file__),HERE/'probe_v1.py']+rules.SOURCE_DEPENDENCIES);rows=[];reviews=[]
 canonical=[c for i in [0,1]for c in rules.layouts(rules.RECIPES[0],i)if c['route_spec']['id']=='east-then-dead-west']
 for c,r,ev in e.run(canonical,'canonical-prototype'):
  q=rules.purpose(c,r);row=report(c,r,ev);row['purpose']=q;rows.append(row)
  if q['ok']:
   v=__import__('copy').deepcopy(c);v['factory_id']=digest(c);v['factory_evidence']=ev;v['recorded_frames']=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in r['frames']];v['review_alias']=c['id'];v['module_sha256']=module_hash(v);reviews.append(v)
 write(e.out/'review_cases.json',dict(cases=reviews,scope='early prototype only; no full calibration/holdout or candidate admission'))
 alts=[v for i in [0,1]for c in rules.layouts(rules.RECIPES[0],i)if c['route_spec']['id']in ['east-air','west-air']for v in rules.alternatives(c)if v['counterexample_kind'].startswith('omit-shot-')]
 for c,r,ev in e.run(alts,'omitted-shot-counters'):
  q=rules.purpose(c,r);row=report(c,r,ev);row['purpose']=q;rows.append(row);print(json.dumps(dict(id=c['id'],safe=r.get('ok'),shots=r.get('shots'),purpose=q,evidence=ev)),flush=True)
 write(e.out/'probe-results.json',rows);write(e.out/'summary.json',dict(actual_cases=e.sim.cases,canonical_prototypes=len(reviews),counter_cases=len(alts),safe_counters=[dict(id=x['case']['id'],purpose=x['purpose'],summary=x['summary'])for x in rows if 'counter-'in x['case']['id']and x['result'].get('ok')],scope='finite actual omitted shot cases; published movement sequence is not forced'))
