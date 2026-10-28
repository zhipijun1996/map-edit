import argparse,json
from pathlib import Path
from . import fixtures_v2 as fixtures
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate,evaluate
from pcg.prototype.creative_batches.batch30_d04_validation.run_v1 import public_witness
HERE=Path(__file__).parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--stage',choices=['screen','full'],required=True);a=p.parse_args();selection=HERE/'frozen-controller-v2.json';deps=[Path(__file__),Path(fixtures.__file__),*fixtures.SOURCE_DEPENDENCIES,Path(public_witness.__code__.co_filename)]
 if a.stage=='full':deps.append(selection)
 e=WorkshopEngine(ROOT/'results'/a.name,extra_sources=deps,runner_script=fixtures.RUNNER_SCRIPT);base=fixtures.fixture()
 if a.stage=='screen':
  rows=[];cases=[base]+[instantiate(base,271029501,l,i)for l in ['mild','moderate']for i in range(3)]
  for c,r,ev in e.run(cases,'final-controller-clean-noise'):
   q=fixtures.purpose(c,r);row=dict(id=c['id'],purpose=q,evidence=ev,result={k:r.get(k)for k in ['ok','reason','shots','jumps','ticks']});rows.append(row);print(json.dumps(row),flush=True)
  rates={l:sum(r['purpose']['ok']for r in rows if '-'+l+'-'in r['id'])/3 for l in ['mild','moderate']};passing=rows[0]['purpose']['ok']and rates['mild']>=.8 and rates['moderate']>=.65
  write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,purpose_passed=sum(r['purpose']['ok']for r in rows),rates=rates,retained=passing,rows=rows,new_modules=0))
  write(selection,dict(control=2 if passing else None,selected_before_calibration_holdout=True,source_run=str(e.out.relative_to(ROOT.parent)),rates=rates));return
 chosen=json.loads(selection.read_text())['control'];cases=[base]if chosen==2 else[]
 cal=evaluate(e,cases,271029501,12,'exact-seam-calibration',fixtures.purpose)if cases else[];write(e.out/'calibration.json',cal)
 retained=[r['case']for r in cal if r['quality_gate']['status']=='awaiting_human_review'];write(e.out/'frozen-before-held.json',dict(case_ids=[c['id']for c in retained],held_seed=271029502))
 write(e.out/'review_cases.json',dict(cases=[public_witness(r)for r in cal if r['quality_gate']['status']=='awaiting_human_review'],scope='Exact two existing immutable modules; not candidate enrollment'))
 held=evaluate(e,retained,271029502,12,'exact-seam-independent-holdout',fixtures.purpose)if retained else[];write(e.out/'holdout.json',held)
 write(e.out/'receipt.json',dict(schema='pcg/N04-exact-Block-seam-full/v2',actual_cases=e.sim.cases,prior_cases=40,all_actual_cases=40+e.sim.cases,maximum_all_actual_cases=160,qualified_fixtures=sum(r['quality_gate']['status']=='awaiting_human_review'for r in held),calibration=cal,holdout=held,new_modules=0,generic_seam='UNKNOWN',production_admitted=False))
if __name__=='__main__':main()
