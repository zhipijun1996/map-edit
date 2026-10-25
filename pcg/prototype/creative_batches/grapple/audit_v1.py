import json,copy
from pathlib import Path
from pcg.prototype.creative_batches.grapple import recipes_v3 as R
from pcg.prototype.workshop.engine import WorkshopEngine,ROOT
from pcg.prototype.workshop.rules import cmd,settle
if __name__=='__main__':
 c=R.candidates('jump-refill')[0];cs=[]
 for hold in [12,24,36,48]:
  for delay in [0,4,8]:
   v=copy.deepcopy(c);v['id']+=f'-counter-direct-single-hook-{hold}-{delay}';v['counterexample_kind']='direct-single-hook';v['control_plan']=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',hold),cmd('grapple',delay,aim_target=[210,40]),R.gate('jump','hook_hang',3),cmd('jump_release',12),cmd('jump',20),cmd('jump_release',12),settle(450,5)];cs.append(v)
 engine=WorkshopEngine(ROOT/'results/workshop-creative-grapple-jump-audit-v1',extra_sources=[Path(__file__),Path(R.__file__),R.RUNNER],runner_script=R.RUNNER.resolve());rows=[]
 for c,r,e in engine.run(cs,'additional-counter'):
  rows.append(dict(id=c['id'],ok=r['ok'],purpose=R.purpose(c,r),evidence=e));print(rows[-1],flush=True)
 (engine.out/'summary.json').write_text(json.dumps(rows))
