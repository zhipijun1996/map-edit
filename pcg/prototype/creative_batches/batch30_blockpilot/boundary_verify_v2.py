"""Use the original Engine, perturbations and regular gate for one exact seam."""
import argparse,json
from pathlib import Path
from . import boundary_v2 as fixture
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
from pcg.prototype.workshop.evaluate import instantiate,evaluate

def main():
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args()
    out=ROOT/'results'/a.name
    if out.exists():raise ValueError('immutable_boundary_run_exists')
    protocol=json.loads((Path(__file__).parent/'boundary-protocol-v2.json').read_text())
    engine=WorkshopEngine(out,extra_sources=[Path(__file__),Path(fixture.__file__),*fixture.SOURCE_DEPENDENCIES],runner_script=fixture.RUNNER_SCRIPT)
    c=fixture.case();write(out/'protocol.json',protocol);write(out/'review_cases.json',dict(cases=[c]))
    rows=[]
    screen=[c]+[instantiate(c,protocol['screen_seed'],level,i)for level in ['mild','moderate']for i in range(6)]
    for v,r,e in engine.run(screen,'screen'):
        q=fixture.purpose(v,r);rows.append(dict(id=v['id'],purpose=q,evidence=e))
    write(out/'screen.json',rows)
    stages={};passed=all(r['purpose']['ok']for r in rows)
    if passed:
        for stage,key in [('calibration','calibration_seed'),('holdout','holdout_seed')]:
            entries=evaluate(engine,[c],protocol[key],protocol['full_trials'],stage,purpose_fn=fixture.purpose)
            write(out/(stage+'.json'),entries);stages[stage]=dict(stats=entries[0]['stats'],quality_gate=entries[0]['quality_gate'])
            if entries[0]['quality_gate']['status']!='awaiting_human_review':passed=False;break
    summary=dict(schema='pcg/exact-block-boundary-verification/v2',passed=passed,actual_physics_cases=engine.sim.cases,screen_passed=sum(r['purpose']['ok']for r in rows),screen_total=len(rows),stages=stages,fixture_version=c['boundary_fixture']['fixture_version'],new_modules=0,generic_seams='UNKNOWN',mirrored_challenge='UNKNOWN',source_B_to_A='UNKNOWN',production_admitted=False)
    assert engine.sim.cases<=protocol['maximum_additional_cases']
    write(out/'summary.json',summary);print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
