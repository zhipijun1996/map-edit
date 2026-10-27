import argparse,json
from pathlib import Path
from . import rules_v1 as rules,alternatives_v1 as counters
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
HERE=Path(__file__).parent

def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['noise','counters'],required=True);a=p.parse_args();selection=HERE/'control-selection-v1.json';controls=json.loads(selection.read_text())['controls'];bases=[rules.candidate(t,controls[t])for t in ['B','C']]
 cs=[instantiate(c,271131223,l,k)for c in bases for l in ['mild','moderate']for k in range(3)]if a.stage=='noise'else[v for c in bases for v in counters.preliminary(c)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(counters.__file__),selection,*rules.SOURCE_DEPENDENCIES],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cs,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],purpose=q,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']},evidence=ev)
  if a.stage=='counters':
   o=external_outcome(c,r);row['outcome']=o;row['classification']=counter_classification(c,r,q,o,dict(shots=1,jumps=1))
  rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows),design_refutations=[r['id']for r in rows if r.get('classification',{}).get('invalidates_design')],rows=rows,new_modules=0))
if __name__=='__main__':main()
