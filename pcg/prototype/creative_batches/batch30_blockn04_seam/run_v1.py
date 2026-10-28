import argparse,json
from pathlib import Path
from . import fixtures_v1 as fixtures
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate,evaluate
from pcg.prototype.creative_batches.batch30_d04_validation.run_v1 import public_witness
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['clean','noise','full'],required=True);a=p.parse_args();selection=HERE/'control-selection-v1.json';deps=[Path(__file__),Path(fixtures.__file__),*fixtures.SOURCE_DEPENDENCIES]
 if a.stage!='clean':deps.append(selection)
 if a.stage=='full':deps += [HERE/'frozen-controller-v1.json',Path(public_witness.__code__.co_filename)]
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=deps,runner_script=fixtures.RUNNER_SCRIPT)
 if a.stage in ['clean','noise']:
  controls=[0,1]if a.stage=='clean'else json.loads(selection.read_text())['clean_valid_controls']
  cs=[fixtures.fixture(k)for k in controls]if a.stage=='clean'else[instantiate(fixtures.fixture(k),271029501,l,i)for k in controls for l in ['mild','moderate']for i in range(3)]
  rows=[]
  for c,r,ev in e.run(cs,'exact-Block-seam-'+a.stage):
   q=fixtures.purpose(c,r);v=dict(id=c['id'],case=c,purpose=q,evidence=ev,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']});rows.append(v);print(json.dumps(dict(id=c['id'],purpose=q,result=v['result'])),flush=True)
  write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows),rows=rows,new_modules=0))
  if a.stage=='clean':
   if selection.exists():raise ValueError('immutable clean selection exists')
   write(selection,dict(schema='pcg/N04-seam-control-selection/v1',clean_valid_controls=[r['case']['seam_specimen']['control']for r in rows if r['purpose']['ok']],source_run=str(e.out.relative_to(ROOT.parent)),chosen_before_noise=True))
  else:
   good=[]
   for k in controls:
    data=[r for r in rows if r['case']['seam_specimen']['control']==k];rates={l:sum(r['purpose']['ok']for r in data if '-'+l+'-'in r['id'])/3 for l in ['mild','moderate']}
    if rates['mild']>=.8 and rates['moderate']>=.65:good.append(k)
   write(HERE/'frozen-controller-v1.json',dict(control=min(good)if good else None,source_run=str(e.out.relative_to(ROOT.parent)),selected_before_full_and_holdout=True))
  return
 chosen=json.loads((HERE/'frozen-controller-v1.json').read_text())['control'];cases=[fixtures.fixture(chosen)]if chosen is not None else[]
 cal=evaluate(e,cases,271029501,12,'exact-seam-calibration',fixtures.purpose)if cases else[];write(e.out/'calibration.json',cal)
 retained=[r['case']for r in cal if r['quality_gate']['status']=='awaiting_human_review'];write(e.out/'frozen-before-held.json',dict(case_ids=[c['id']for c in retained],held_seed=271029502))
 write(e.out/'review_cases.json',dict(cases=[public_witness(r)for r in cal if r['quality_gate']['status']=='awaiting_human_review'],scope='One exact continuous two-source fixture, not new Module enrollment'))
 held=evaluate(e,retained,271029502,12,'exact-seam-independent-holdout',fixtures.purpose)if retained else[];write(e.out/'holdout.json',held)
 write(e.out/'receipt.json',dict(schema='pcg/N04-exact-Block-seam-full/v1',actual_cases=e.sim.cases,qualified_fixtures=sum(r['quality_gate']['status']=='awaiting_human_review'for r in held),calibration=cal,holdout=held,new_modules=0,generic_seam='UNKNOWN',production_admitted=False))
if __name__=='__main__':main()
