"""Bounded tail control repair; reuse original Godot/evaluate/quality gates."""
import argparse
import json
from pathlib import Path
from pcg.prototype.creative_batches.batch30_d04 import api_v3 as api
from pcg.prototype.workshop.engine import ROOT, WorkshopEngine
from pcg.prototype.workshop.evaluate import evaluate, instantiate
from pcg.prototype.workshop.experiments import write
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest
from .run_v1 import purpose, public_witness
from . import repair_rules_v1 as rules

HERE = Path(__file__).parent


def run(name):
    p = json.loads((HERE/'repair-protocol-v1.json').read_text())
    old = ROOT/'results/workshop-batch30-d04-full-fixtures-v2'
    if not (old/'summary.json').exists():
        raise ValueError('Finish the previous registered cycle before repair execution')
    # Read calibration only; the previous cycle held data never choose repair
    # parameters or candidates. Its summary is used solely for cost accounting.
    spent = json.loads((old/'summary.json').read_text())['actual_cases']
    calibration_old = json.loads((old/'calibration-evaluations.json').read_text())
    assert p['root_forward_actual_cases'] + spent + p['maximum_new_cases'] <= p['maximum_relationship_total']
    e = WorkshopEngine(ROOT/'results'/name, extra_sources=[Path(__file__), Path(rules.__file__), HERE/'repair-protocol-v1.json', HERE/'run_v1.py', Path(purpose.__code__.co_filename)] + rules.SOURCE_DEPENDENCIES)
    write(e.out/'protocol.json', dict(p, prior_fixture_actual_cases=spent))
    bases = [rules.materialize(i,k) for i in range(2) for k in range(2)]
    probes = []
    for c in bases:
        probes += [c] + [instantiate(c,p['calibration_seed'],level,j) for level in ['mild','moderate'] for j in range(2)]
    write(e.out/'source-candidates.json',dict(cases=bases))
    probe_rows=[]
    clean_ok=set()
    for c,r,ev in e.run(probes,'tail-control-probe'):
        check=purpose(c,r)
        probe_rows.append(dict(id=c['id'],purpose=check,evidence=ev))
        if '-mild-' not in c['id'] and '-moderate-' not in c['id'] and check['ok']:
            clean_ok.add(c['id'])
    write(e.out/'probe-results.json',probe_rows)
    cal=evaluate(e,[c for c in bases if c['id'] in clean_ok],p['calibration_seed'],12,'tail-calibration',purpose_fn=purpose)
    write(e.out/'calibration-evaluations.json',cal)
    selected=[]
    choices=[]
    def rank(x):
        return (min(x['stats'][l]['rate'] for l in ['mild','moderate']),sum(x['stats'][l]['rate'] for l in ['clean','mild','moderate']))
    for interface in range(2):
        mids=[x for x in calibration_old if x['case']['interface']==interface and x['case']['expected_reward']==0 and x['quality_gate']['status']=='awaiting_human_review']
        rewards=[x for x in cal if x['case']['interface']==interface and x['quality_gate']['status']=='awaiting_human_review']
        mid=max(mids,key=lambda x:(*rank(x),-x['case']['rule_parameters']['return_control']['index'])) if mids else None
        reward=max(rewards,key=lambda x:(*rank(x),-x['case']['rule_parameters']['return_tail_repair']['candidate_index'])) if rewards else None
        if mid and reward:
            selected += [mid,reward]
        choices.append(dict(interface=interface,middle_id=mid['case']['id'] if mid else None,reward_id=reward['case']['id'] if reward else None,joint_calibration_ok=bool(mid and reward)))
    write(e.out/'selection-before-holdout.json',dict(choices=choices,case_ids=[x['case']['id'] for x in selected],calibration_sha256=file_sha(e.out/'calibration-evaluations.json'),old_calibration_sha256=file_sha(old/'calibration-evaluations.json'),holdout_seed=p['holdout_seed']))
    # Obtain local-source exact clean witnesses for middle fixtures so native
    # recorder needs no implicit cross-run evidence redirect.
    mid_witnesses={}
    for c,r,ev in e.run([x['case'] for x in selected if x['case']['expected_reward']==0],'middle-canonical-clean'):
        assert purpose(c,r)['ok']
        mid_witnesses[c['id']]=dict(case=c,result=r,evidence=ev)
    nominal={x['case']['id']:x['witness']['result'] for x in selected}
    comparison=[]
    for c,r,ev in e.run([v for x in selected if x['case']['expected_reward']==12 for v in api.alternatives(x['case'])],'repaired-tail-counterexample'):
        from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
        interpreted,audit=classify(c,r)
        task=api.fixture_task_outcome(c,interpreted)
        base=nominal[c['id'].split('-counter-')[0]]
        costs=dict(nominal={k:base.get(k) for k in ['shots','jumps','ticks']},alternative={k:r.get(k) for k in ['shots','jumps','ticks']})
        cheaper=bool(task['ok'] and all(r.get(k,10**9)<=base.get(k,-1) for k in ['shots','jumps','ticks']) and any(r.get(k,10**9)<base.get(k,-1) for k in ['shots','jumps','ticks']))
        comparison.append(dict(id=c['id'],same_task=task,costs=costs,pareto_cheaper_refutation_candidate=cheaper,observer_interpretation=audit,evidence=ev))
        if task['ok']:print(json.dumps(comparison[-1]),flush=True)
    write(e.out/'counterexamples.json',comparison)
    reviews=[]
    for x in selected:
        if x['case']['expected_reward']==0:
            x=dict(x,witness=mid_witnesses[x['case']['id']])
        reviews.append(public_witness(x))
    write(e.out/'review_cases.json',dict(cases=reviews,scope='same-world continuous fixtures, not Module enrollment'))
    write(e.out/'media-witnesses-before-holdout.json',dict(review_cases_sha256=file_sha(e.out/'review_cases.json'),selection_sha256=file_sha(e.out/'selection-before-holdout.json')))
    held=evaluate(e,[x['case'] for x in selected],p['holdout_seed'],12,'tail-independent-holdout',purpose_fn=purpose) if selected else []
    write(e.out/'holdout-evaluations.json',held)
    assert e.sim.cases<=p['maximum_new_cases']
    total=p['root_forward_actual_cases']+spent+e.sim.cases
    assert total<=p['maximum_relationship_total']
    summary=dict(schema='pcg/batch30-d04-tail-repair-receipt/v1',actual_new_cases=e.sim.cases,prior_fixture_cases=spent,forward_cases=p['root_forward_actual_cases'],relationship_total_cases=total,choices=choices,calibration=[dict(id=x['case']['id'],stats=x['stats'],quality_gate=x['quality_gate']) for x in cal],holdout=[dict(id=x['case']['id'],stats=x['stats'],quality_gate=x['quality_gate']) for x in held],same_task_counter_successes=[x for x in comparison if x['same_task']['ok']],pareto_cheaper_refutation_candidates=[x['id'] for x in comparison if x['pareto_cheaper_refutation_candidate']],unchanged_world_adaptive_counter_run=str(old.relative_to(ROOT)),actual_new_modules=0,human_approval='UNKNOWN',production_admitted=False,whole_map='UNKNOWN',generic_return_transfer='UNKNOWN',source_binding_sha256=file_sha(e.out/'source_binding.json'))
    write(e.out/'summary.json',summary)
    print(json.dumps(dict(actual_new_cases=e.sim.cases,relationship_total_cases=total,choices=choices,held_passed=sum(x['quality_gate']['status']=='awaiting_human_review' for x in held),held_routes=len(held))),flush=True)
    return e.out


if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--name',required=True);args=a.parse_args();run(args.name)
