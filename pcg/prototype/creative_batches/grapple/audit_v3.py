import json,copy
from pathlib import Path
from pcg.prototype.creative_batches.grapple import recipes_v8 as R
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import cmd,settle
if __name__=='__main__':
 c=R.candidates('hang-recast')[0];cs=[]
 for hold in [0,8,12,16,20,24,30,36,48]:
  for after in [0,3]:
   v=copy.deepcopy(c);v['id']+=f'-counter-expanded-first-ring-{hold}-{after}';v['counterexample_kind']='expanded-first-ring-only';v['control_plan']=copy.deepcopy(c['control_plan'][:5])+[cmd('axis',value=-1),R.gate('jump','hook_hang',after),cmd('jump_release',hold),settle(-100,6)];cs.append(v)
 engine=WorkshopEngine(ROOT/'results/workshop-creative-grapple-recast-audit-v1',extra_sources=[Path(__file__),Path(R.__file__),R.RUNNER],runner_script=R.RUNNER.resolve());rows=[]
 for c,r,e in engine.run(cs,'expanded-first-ring-counter'):
  rows.append(dict(id=c['id'],ok=r['ok'],purpose=R.purpose(c,r),evidence=e));print(rows[-1],flush=True)
 (engine.out/'summary.json').write_text(json.dumps(rows))
