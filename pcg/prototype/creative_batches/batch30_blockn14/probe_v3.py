import argparse,json
from pathlib import Path
from . import rules_v2 as rules,alternatives_v1 as counters
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',required=True,choices=['noise','counters']);a=p.parse_args();sel=HERE/'control-selection-v1.json';choice=json.loads(sel.read_text())['controls'];bases=[rules.candidate(t,choice[t])for t in ['B','C']]
 cs=[instantiate(c,271131425,l,k)for c in bases for l in ['mild','moderate']for k in range(6)]if a.stage=='noise'else[v for c in bases for v in counters.preliminary(c)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(counters.__file__),sel,*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,margin=rules.margin(c,r),result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if a.stage=='counters':row['classification']=counter_classification(c,r,q,external_outcome(c,r),dict(shots=1,jumps=2))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows),design_refutations=[r['id']for r in rows if r.get('classification',{}).get('invalidates_design')],rows=rows,new_modules=0))
if __name__=='__main__':main()
