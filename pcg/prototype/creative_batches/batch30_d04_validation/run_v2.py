"""Continuous D04 fixtures through the original evaluator and real Harness."""
import argparse
import copy
import json
from pathlib import Path

from pcg.prototype.creative_batches.batch30_d04 import api_v3 as api
from pcg.prototype.creative_batches.batch30_d04 import adaptive_counters_v1 as adaptive
from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest, module_hash
from pcg.prototype.workshop.engine import ROOT, WorkshopEngine
from pcg.prototype.workshop.evaluate import evaluate
from pcg.prototype.workshop.experiments import write

HERE = Path(__file__).parent


def purpose(case, raw):
    interpreted, audit = classify(case, raw)
    check = api.purpose(case, interpreted)
    check['causal']['observer_interpretation'] = audit
    return check


def public_witness(entry):
    w = entry['witness']
    c = copy.deepcopy(w['case'])
    c['factory_id'] = digest(entry['case'])
    c['factory_evidence'] = w['evidence']
    c['recorded_frames'] = [dict(frame=f['frame'], axis=f['axis'], requested=f['requested']) for f in w['result']['frames']]
    c['validation_summary'] = entry['stats']
    c['review_alias'] = entry['case']['id']
    c['module_sha256'] = module_hash(c)
    return c


def run(name):
    protocol = json.loads((HERE / 'protocol-v2.json').read_text())
    e = WorkshopEngine(ROOT / 'results' / name, extra_sources=[Path(__file__), HERE / 'protocol-v2.json', HERE / 'run_v1.py', Path(api.__file__), Path(adaptive.__file__), Path(classify.__code__.co_filename)] + api.SOURCE_DEPENDENCIES + adaptive.SOURCE_DEPENDENCIES)
    write(e.out / 'protocol.json', protocol)
    bases = [api.fixtures(1,k)[0] for k in range(4)] + [api.fixtures(1,0)[1]]
    write(e.out / 'source-candidates.json', dict(cases=bases))
    new_calibration = evaluate(e, bases, protocol['calibration_seed'], 12, 'fixture-calibration', purpose_fn=purpose)
    prior = ROOT / 'results' / protocol['prior_run']
    prior_entries = json.loads((prior / 'evaluations.json').read_text())
    prior_submitted = sum(len(json.loads(p.read_text())['cases']) for p in (prior/'physics').glob('*.input.json'))
    for x in prior_entries:
        x['evidence_source_run'] = str(prior.relative_to(ROOT))
    calibration = prior_entries + new_calibration
    def programme_sha(c):
        from pcg.prototype.factory.core.quality import candidate_hash
        return digest(dict(original_candidate_hash=candidate_hash(c), latches=c['latches'], rewards=c['reward_sites'], enemies=c.get('enemies',[])))
    equivalences=[]
    for i in range(2):
        rep=next(x for x in calibration if x['case']['interface']==i and x['case']['expected_reward']==12)
        for k in range(4):
            c=api.fixtures(i,k)[1]
            assert programme_sha(c)==programme_sha(rep['case'])
            equivalences.append(dict(case_id=c['id'],actual_representative_case_id=rep['case']['id'],physical_programme_sha256=programme_sha(c),evidence_source_run=rep.get('evidence_source_run',str(e.out.relative_to(ROOT))),equivalence_only_not_new_physics=True))
    write(e.out/'equivalent-programmes.json',equivalences)
    write(e.out / 'calibration-evaluations.json', calibration)
    choices = []
    selected = []
    for interface in range(2):
        eligible = []
        for control in range(4):
            group = [x for x in calibration if x['case']['interface'] == interface and x['case']['expected_reward']==0 and x['case']['rule_parameters']['return_control']['index'] == control] + [next(x for x in calibration if x['case']['interface']==interface and x['case']['expected_reward']==12)]
            if len(group) == 2 and all(x['quality_gate']['status'] == 'awaiting_human_review' for x in group):
                rates = [x['stats'][level]['rate'] for x in group for level in ['mild', 'moderate']]
                eligible.append((min(rates), sum(x['stats'][l]['rate'] for x in group for l in ['clean', 'mild', 'moderate']), -control, group))
        best = max(eligible, key=lambda x: x[:3]) if eligible else None
        chosen = best[3] if best else []
        selected += chosen
        choices.append(dict(interface=interface, selected_control=-best[2] if best else None, selected_case_ids=[x['case']['id'] for x in chosen], eligible_controls=[-x[2] for x in eligible], status='selected_before_holdout' if best else 'needs_design'))
    write(e.out / 'selection-before-holdout.json', dict(choices=choices, calibration_sha256=file_sha(e.out / 'calibration-evaluations.json'), canonical_case_sha256=[digest(x['witness']['case']) for x in selected], holdout_seed=protocol['holdout_seed']))
    # Counters are still useful when robustness rejects a control; compare the
    # authored default then, clearly excluded from selected/held/admitted.
    counter_bases = []
    for i in range(2):
        group = [x for x in selected if x['case']['interface'] == i]
        counter_bases += [x['case'] for x in group] if group else api.fixtures(i)
    nominal = {c['id']: next((x['witness']['result'] for x in calibration if x['case']['id'] == c['id'] and x.get('witness')), None) for c in counter_bases}
    comparisons = []
    counters = [v for c in counter_bases for v in api.alternatives(c)] + [v for i in range(2) for v in adaptive.cases(i)]
    for c, raw, ev in e.run(counters, 'same-task-counterexample'):
        result, audit = classify(c, raw)
        outcome = api.fixture_task_outcome(c, result)
        base = nominal.get(c['id'].split('-counter-')[0])
        if c.get('counter_task_scope'):
            reward_base = next((x for x in counter_bases if x['interface'] == c['interface'] and x['expected_reward'] == 12), None)
            base = nominal.get(reward_base['id']) if reward_base else None
        costs = dict(nominal={k: base.get(k) for k in ['shots', 'jumps', 'ticks']} if base else None, alternative={k: result.get(k) for k in ['shots', 'jumps', 'ticks']})
        cheaper = bool(outcome['ok'] and base and all(result.get(k, 10**9) <= base.get(k, -1) for k in ['shots', 'jumps', 'ticks']) and any(result.get(k, 10**9) < base.get(k, -1) for k in ['shots', 'jumps', 'ticks']))
        row = dict(id=c['id'], kind=c['counterexample_kind'], same_task=outcome, costs=costs, pareto_cheaper_refutation_candidate=cheaper, observer_interpretation=audit, purpose=purpose(c, raw), evidence=ev)
        comparisons.append(row)
        if outcome['ok']:
            print(json.dumps(dict(id=c['id'], same_task=True, costs=costs, pareto_cheaper_refutation_candidate=cheaper)), flush=True)
    write(e.out / 'counterexamples.json', comparisons)
    # Freeze media witnesses before reading held results; these are fixtures,
    # never enrollments or additional exported Module directions.
    reviews = [public_witness(x) for x in selected]
    write(e.out / 'review_cases.json', dict(cases=reviews, scope='validation-only continuous A return fixtures; not counted as Module'))
    write(e.out / 'media-witnesses-before-holdout.json', dict(review_cases_sha256=file_sha(e.out / 'review_cases.json'), selection_sha256=file_sha(e.out / 'selection-before-holdout.json')))
    held = evaluate(e, [x['case'] for x in selected], protocol['holdout_seed'], 12, 'fixture-holdout', purpose_fn=purpose) if selected else []
    write(e.out / 'holdout-evaluations.json', held)
    assert e.sim.cases + prior_submitted <= protocol['maximum_actual_cases']
    summary = dict(schema='pcg/batch30-d04-fixture-receipt/v1', actual_cases=e.sim.cases+prior_submitted, new_actual_cases=e.sim.cases, prior_submitted_conservative_cases=prior_submitted, planned_bound=880, choices=choices, calibration=[dict(id=x['case']['id'], stats=x['stats'], quality_gate=x['quality_gate']) for x in calibration], holdout=[dict(id=x['case']['id'], stats=x['stats'], quality_gate=x['quality_gate']) for x in held], same_task_counter_successes=[x for x in comparisons if x['same_task']['ok']], pareto_cheaper_refutation_candidates=[x['id'] for x in comparisons if x['pareto_cheaper_refutation_candidate']], new_modules=0, production_admitted=False, human_approval='UNKNOWN', generic_return='UNKNOWN', all_failures_preserved=True, source_binding_sha256=file_sha(e.out / 'source_binding.json'))
    write(e.out / 'summary.json', summary)
    print(json.dumps(dict(actual_cases=e.sim.cases+prior_submitted, choices=choices, held_passed=sum(x['quality_gate']['status'] == 'awaiting_human_review' for x in held), held_routes=len(held), counter_successes=len(summary['same_task_counter_successes']), cheaper=len(summary['pareto_cheaper_refutation_candidates']))), flush=True)
    return e.out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--name', required=True)
    a = p.parse_args()
    run(a.name)
