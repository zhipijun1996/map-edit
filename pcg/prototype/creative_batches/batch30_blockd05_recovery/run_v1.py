import argparse,json
from pathlib import Path
from . import rules_v1 as rules
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import evaluate
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['clean','full'],required=True);p.add_argument('--selection',type=Path,default=HERE/'control-selection-v1.json');a=p.parse_args();protocol=rules.PROTOCOL
 deps=[Path(__file__),Path(rules.__file__),*rules.SOURCE_DEPENDENCIES]
 if a.mode=='full':deps.append(a.selection.resolve())
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=deps,runner_script=rules.RUNNER_SCRIPT)
 if a.mode=='clean':
  rows=[]
  for c,r,ev in e.run([rules.fixture(i,k)for i in [0,1]for k in range(4)],'bounded-recovery-clean'):
   q=rules.purpose(c,r);row=dict(id=c['id'],case=c,purpose=q,evidence=ev,result={k:r.get(k)for k in ['ok','reason','hp','shots','jumps','ticks']});rows.append(row);print(json.dumps(dict(id=c['id'],purpose=q,result=row['result'])),flush=True)
  selected={}
  for i in [0,1]:
   good=[r for r in rows if r['case']['interface']==i and r['purpose']['ok']]
   if good:selected[str(i)]=min(r['case']['validation_fixture']['control']for r in good)
  if a.selection.exists():raise ValueError('immutable selection exists')
  write(a.selection,dict(schema='pcg/block-D05-recovery-control-selection/v1',controls=selected,selected_before_full_calibration=True,source_run=str(e.out.relative_to(ROOT.parent))))
  write(e.out/'screen.json',dict(actual_cases=e.sim.cases,rows=rows,controls=selected,new_modules=0));return
 selection=json.loads(a.selection.read_text());cases=[rules.fixture(int(i),k)for i,k in selection['controls'].items()]
 cal=evaluate(e,cases,protocol['calibration_seed'],12,'recovery-calibration',rules.purpose)if cases else[]
 write(e.out/'calibration.json',cal)
 chosen=[v['case']for v in cal if v['quality_gate']['status']=='awaiting_human_review']
 write(e.out/'frozen-before-held.json',dict(selected=chosen,actual_cases_before_holdout=e.sim.cases,selection='Already fixed lowest clean valid control; no calibration fallback'))
 held=evaluate(e,chosen,protocol['holdout_seed'],12,'recovery-independent-holdout',rules.purpose)if chosen else[]
 write(e.out/'holdout.json',held)
 previous=protocol['prior_failed_clean_cases']+8
 value=dict(schema='pcg/block-D05-independent-recovery-receipt/v1',actual_new_full_cases=e.sim.cases,prior_cases=previous,actual_cases_total=previous+e.sim.cases,maximum_cases_total=protocol['maximum_actual_cases_total'],qualified_versions=[v['case']['validation_fixture']['source_contentVersion']for v in held if v['quality_gate']['status']=='awaiting_human_review'],calibration=cal,holdout=held,new_modules=0,human_fun='UNKNOWN',production_admitted=False)
 assert value['actual_cases_total']<=protocol['maximum_actual_cases_total']
 write(e.out/'receipt.json',value)
if __name__=='__main__':main()
