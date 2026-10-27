import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose,external_outcome,counter_classification
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['noise','counters','D-clean','D-noise'],required=True);a=p.parse_args();entries=['D']if a.stage.startswith('D')else['A'];source=[rules.candidate(entry,target,.2)for entry in entries for target in ['B','C']]
 if a.stage=='counters':cases=[v for c in source for v in rules.alternatives(c)]
 elif a.stage=='D-clean':cases=source
 else:cases=[instantiate(c,271028903,level,i)for c in source for level in ['mild','moderate']for i in range(2 if a.stage=='D-noise'else 4)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'control-selection-v1.json'],runner_script=rules.RUNNER_SCRIPT);rows=[]
 for c,r,ev in e.run(cases,a.stage):
  q=checked_purpose(rules,c,r);row=dict(id=c['id'],case=c,purpose=q,evidence=ev,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']})
  if a.stage=='counters':row['classification']=counter_classification(c,r,q,external_outcome(c,r))
  rows.append(row);print(json.dumps(dict(id=c['id'],purpose=q,result=row['result'],classification=row.get('classification'))),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(v['purpose']['ok']for v in rows),design_refutations=sum(v.get('classification',{}).get('invalidates_design',False)for v in rows),rows=rows,new_modules=0))
if __name__=='__main__':main()
