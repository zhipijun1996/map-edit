import json
from pathlib import Path
from . import rules_v2 as rules,comparisons_v1 as comparison
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
HERE=Path(__file__).parent

def main():
 sel=HERE/'control-selection-v1.json';k=json.loads(sel.read_text())['chosen_control'];base=rules.candidate(k,'loop');cs=comparison.loop_alternatives(base)
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn08-comparisons-v1',extra_sources=[Path(__file__),Path(comparison.__file__),sel,*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,'same-task-counter'):
  q=checked_purpose(rules,c,r);o=comparison.task_outcome(c,r);cl=comparison.classify(c,r,q,o,dict(shots=4,jumps=4));row=dict(id=c['id'],purpose=q,outcome=o,classification=cl,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,design_refutations=[r['id']for r in rows if r['classification']['invalidates_design']],shortcut_claim='UNKNOWN until actual cost comparison; old route allowed',new_modules=0))
if __name__=='__main__':main()
