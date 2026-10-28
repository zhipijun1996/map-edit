"""Fixed exact D04r2 continuous fixtures, original evaluator and Harness."""
import argparse,json
from pathlib import Path
from pcg.prototype.creative_batches.batch30_d04r2 import api_v1 as api
from pcg.prototype.creative_batches.batch30_d04_validation.run_v1 import purpose,public_witness
from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.evaluate import evaluate
from pcg.prototype.workshop.experiments import write

HERE=Path(__file__).parent


def run(name):
    protocol=json.loads((HERE/'protocol-v1.json').read_text())
    e=WorkshopEngine(ROOT/'results'/name,extra_sources=[Path(__file__),HERE/'protocol-v1.json',Path(api.__file__),Path(purpose.__code__.co_filename),Path(classify.__code__.co_filename)]+api.SOURCE_DEPENDENCIES)
    write(e.out/'protocol.json',protocol)
    bases=[c for i in range(2)for c in api.fixtures(i)]
    write(e.out/'source-candidates.json',dict(cases=bases))
    calibration=evaluate(e,bases,protocol['calibration_seed'],12,'continuous-calibration',purpose_fn=purpose)
    write(e.out/'calibration-evaluations.json',calibration)
    all_cal_ok=all(x['quality_gate']['status']=='awaiting_human_review'for x in calibration)
    selected=calibration if all_cal_ok else []
    write(e.out/'selection-before-holdout.json',dict(all_four_calibration_passed=all_cal_ok,selected_case_ids=[x['case']['id']for x in selected],calibration_sha256=file_sha(e.out/'calibration-evaluations.json'),holdout_seed=protocol['holdout_seed']))
    comparisons=[]
    for c,raw,ev in e.run([v for i in range(2)for v in api.adaptive_counters(i)],'same-task-adaptive-counter'):
        r,audit=classify(c,raw)
        outcome=api.fixture_task_outcome(c,r)
        entry=next(x for x in calibration if x['case']['interface']==c['interface']and x['case']['expected_reward']==12)
        baseline=entry['witness']['result']if entry.get('witness')else None
        costs=dict(nominal={k:baseline.get(k)for k in ['shots','jumps','ticks']}if baseline else None,alternative={k:r.get(k)for k in ['shots','jumps','ticks']})
        cheaper=bool(outcome['ok']and baseline and all(r.get(k,10**9)<=baseline.get(k,-1)for k in ['shots','jumps','ticks'])and any(r.get(k,10**9)<baseline.get(k,-1)for k in ['shots','jumps','ticks']))
        row=dict(id=c['id'],same_task=outcome,costs=costs,pareto_cheaper_refutation_candidate=cheaper,evidence=ev,observer_interpretation=audit)
        comparisons.append(row)
        if outcome['ok']:print(json.dumps(row),flush=True)
    write(e.out/'counterexamples.json',comparisons)
    reviews=[public_witness(x)for x in selected]
    write(e.out/'review_cases.json',dict(cases=reviews,scope='Exact continuous fixtures only; not Module enrollment or generic return'))
    write(e.out/'media-witnesses-before-holdout.json',dict(review_cases_sha256=file_sha(e.out/'review_cases.json'),selection_sha256=file_sha(e.out/'selection-before-holdout.json')))
    held=evaluate(e,[x['case']for x in selected],protocol['holdout_seed'],12,'continuous-independent-holdout',purpose_fn=purpose)if selected else []
    write(e.out/'holdout-evaluations.json',held)
    assert e.sim.cases<=protocol['maximum_actual_cases']
    summary=dict(schema='pcg/batch30-d04r2-continuous-receipt/v1',actual_cases=e.sim.cases,calibration=[dict(id=x['case']['id'],stats=x['stats'],quality_gate=x['quality_gate'])for x in calibration],holdout=[dict(id=x['case']['id'],stats=x['stats'],quality_gate=x['quality_gate'])for x in held],all_four_calibration_passed=all_cal_ok,all_four_held_passed=len(held)==4 and all(x['quality_gate']['status']=='awaiting_human_review'for x in held),same_task_counter_successes=[x for x in comparisons if x['same_task']['ok']],pareto_cheaper_refutation_candidates=[x['id']for x in comparisons if x['pareto_cheaper_refutation_candidate']],physics_source_binding_sha256=file_sha(e.out/'source_binding.json'),new_modules=0,generic_return='UNKNOWN',whole_map='UNKNOWN',human_approval='UNKNOWN',production_admitted=False)
    write(e.out/'summary.json',summary)
    print(json.dumps({k:summary[k]for k in ['actual_cases','all_four_calibration_passed','all_four_held_passed','new_modules']}),flush=True)
    return e.out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);a=p.parse_args();run(a.name)
