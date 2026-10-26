import argparse,json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import evaluate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.creative_batches.batch30_d04_validation.run_v1 import public_witness
from . import fixtures_v1 as fixtures

HERE=Path(__file__).parent


def run(name):
    audits=[dict(left_interface=i,right_interface=j,**fixtures.audited_pair(i,j)[2])for i in range(2)for j in range(2)]
    files=[ROOT.parent/path for audit in audits for part in ['source_left','source_right']for path in audit[part]['files']]
    e=WorkshopEngine(ROOT/'results'/name,extra_sources=[Path(__file__),Path(fixtures.__file__),Path(public_witness.__code__.co_filename)]+fixtures.SOURCE_DEPENDENCIES+files,runner_script=fixtures.RUNNER_SCRIPT)
    write(e.out/'protocol.json',json.loads((HERE/'protocol-v2.json').read_text()))
    write(e.out/'placement-audits.json',audits)
    bases=[fixtures.candidate(0,j,k)for j in range(2)for k in range(2)]
    write(e.out/'source-cases.json',dict(cases=bases))
    probes=[];chosen={}
    for c,r,ev in e.run(bases,'true-two-module-seam-probe'):
        q=fixtures.purpose(c,r)
        key=c['seam_specimen']['source_right']['contentVersion']
        probes.append(dict(case=c,check=q,evidence=ev))
        if q['ok']and key not in chosen:chosen[key]=c
        print(json.dumps(dict(id=c['id'],ok=q['ok'],reasons=q['reasons'],shots=r.get('shots'),coins=r.get('workshop',{}).get('coins'),ticks=r.get('ticks'),C01=q['causal']['C01'],D05=q['causal']['D05'])),flush=True)
    write(e.out/'probe-results.json',probes)
    selected=list(chosen.values())
    write(e.out/'selection-after-probes.json',dict(case_ids=[c['id']for c in selected],probe_sha256=file_sha(e.out/'probe-results.json'),scope='Fixed exact Module pairs under declared transforms; first passing controller only'))
    cal=evaluate(e,selected,261033010,12,'seam-calibration',purpose_fn=fixtures.purpose)if selected else []
    write(e.out/'calibration-evaluations.json',cal)
    passing=[x for x in cal if x['quality_gate']['status']=='awaiting_human_review']
    write(e.out/'selection-before-holdout.json',dict(case_ids=[x['case']['id']for x in passing],fixture_versions=[x['case']['seam_specimen']['fixture_version']for x in passing],calibration_sha256=file_sha(e.out/'calibration-evaluations.json'),holdout_seed=261033011))
    write(e.out/'review_cases.json',dict(cases=[public_witness(x)for x in passing],scope='Exact two immutable-module continuous fixtures, not new Module enrollment'))
    write(e.out/'media-witnesses-before-holdout.json',dict(review_cases_sha256=file_sha(e.out/'review_cases.json'),selection_sha256=file_sha(e.out/'selection-before-holdout.json')))
    held=evaluate(e,[x['case']for x in passing],261033011,12,'seam-independent-holdout',purpose_fn=fixtures.purpose)if passing else []
    write(e.out/'holdout-evaluations.json',held)
    assert e.sim.cases<=250
    summary=dict(schema='pcg/batch30-exact-module-seam-result/v1',actual_cases=e.sim.cases,structural_rejections=[x for x in audits if not x['audit']['accepted']],calibration=[dict(id=x['case']['id'],stats=x['stats'],quality_gate=x['quality_gate'])for x in cal],holdout=[dict(id=x['case']['id'],stats=x['stats'],quality_gate=x['quality_gate'])for x in held],technical_scoped_fixtures=sum(x['quality_gate']['status']=='awaiting_human_review'for x in held),new_modules=0,new_families=0,added_solid_area=0,removed_solid_area=0,all_source_solid_union_preserved=True,no_teleport_or_resource_reset=True,generic_seams='UNKNOWN',generic_transforms='UNKNOWN',whole_map='UNKNOWN',human_approval='UNKNOWN',production_admitted=False,source_binding_sha256=file_sha(e.out/'source_binding.json'))
    write(e.out/'summary.json',summary)
    print(json.dumps(dict(actual_cases=e.sim.cases,technical_scoped_fixtures=summary['technical_scoped_fixtures'])),flush=True)
    return e.out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
