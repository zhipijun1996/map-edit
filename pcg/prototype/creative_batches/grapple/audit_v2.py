import json,copy
from pathlib import Path
from pcg.prototype.creative_batches.grapple import recipes_v2 as R
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import cmd
if __name__=='__main__':
 c=R.candidates('hang-phase')[2];cs=[]
 for lo in [0,.125,.25,.375,.5,.625,.75,.875]:
  v=copy.deepcopy(c);v['id']+=f'-counter-entry-phase-{lo}';v['counterexample_kind']='entry-phase';p=[s for s in copy.deepcopy(c['control_plan'])if not s.get('trigger',{}).get('dynamic')];v['control_plan']=[cmd('axis',value=0),dict(op='wait',trigger=dict(dynamic=dict(kind='saw_phase',id='departure-saw',window=[lo,lo+.05]),timeout=240))]+p;cs.append(v)
 engine=WorkshopEngine(ROOT/'results/workshop-creative-grapple-hang-audit-v1',extra_sources=[Path(__file__),Path(R.__file__),R.RUNNER],runner_script=R.RUNNER.resolve());rows=[]
 for c,r,e in engine.run(cs,'entry-wait-counter'):
  rows.append(dict(id=c['id'],ok=r['ok'],purpose=R.purpose(c,r),evidence=e));print(rows[-1],flush=True)
 (engine.out/'summary.json').write_text(json.dumps(rows))
