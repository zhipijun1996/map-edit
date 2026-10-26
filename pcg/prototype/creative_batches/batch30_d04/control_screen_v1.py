"""Search another already declared v5 control after pre-calibration feedback."""
import json
from pathlib import Path
from . import api_v1 as api
from . import rules_v5 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
bases=[api.prepare(rules.materialize(1,'middle','outbound',3)),api.prepare(rules.materialize(1,'reward','reward-return',3))]
cs=[instantiate(c,261026904,'mild',i)for c in bases for i in range(6)]
e=WorkshopEngine(ROOT/'results/workshop-batch30-d04-v5-control3-screen-v1',extra_sources=[Path(__file__),Path(api.__file__)]+api.SOURCE_DEPENDENCIES);rows=[]
for c,r,ev in e.run(cs,'existing-control3-screen'):
 q=api.purpose(c,r);rows.append(dict(id=c['id'],ok=q['ok'],purpose=q,evidence=ev));print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'])),flush=True)
write(e.out/'summary.json',dict(actual_cases=e.sim.cases,passed=sum(r['ok']for r in rows),rows=rows))
