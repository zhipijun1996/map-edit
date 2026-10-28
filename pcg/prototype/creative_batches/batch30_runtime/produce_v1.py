"""Register bounded recipes on the existing production/evaluation/store path."""
import argparse
import importlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace

from pcg.prototype.creative_batches.plains50_ports.produce_v2 import run
from pcg.prototype.creative_batches.junctions.landing_buffer_v1 import classify
from pcg.prototype.creative_batches.junctions.produce_v1 import external_outcome as visit_outcome
from pcg.prototype.workshop.production_loop import static_preflight

HERE = Path(__file__).parent
PCG = HERE.parents[2]
REPO = PCG.parent
CELL = HERE.parent / 'batch30_cell'


def normalized(case, result):
    return classify(case, result)


def external_outcome(case, result):
    result, interpretation = normalized(case, result)
    outcome = visit_outcome(case, result)
    claimed = {e['id'] for e in result.get('workshop', {}).get('events', [])
               if e.get('type') == 'chest_claim' and e.get('accepted')}
    required = set(case.get('required_rewards', case.get('route_spec', {}).get('required_rewards', [])))
    allowed = not any(result.get(k, 0) for k in ['air_jumps', 'wall_jumps', 'grapples'])
    outcome.update(required_reward_ids=sorted(required), claimed_reward_ids=sorted(claimed),
                   ability_contract_satisfied=allowed, observer_interpretation=interpretation)
    outcome['ok'] = outcome['ok'] and required <= claimed and allowed and result.get('hp')==5 and not result.get('plains',{}).get('player_damage') and not result.get('returns')
    park=case.get('required_carrier_park')
    if park:
        final=result.get('frames',[{}])[-1]
        platform=next((p for p in final.get('moving_platforms',[])if p['id']==park['id']),None)
        state=next((p for p in result.get('workshop',{}).get('carriers',[])if p['id']==park['id']),None)
        x=platform['position'][0]if platform else None
        valid=bool(state and x is not None and state['running']==park['running']and park['x_range'][0]<=x<=park['x_range'][1])
        outcome.update(required_carrier_park=park,observed_carrier_x=x,observed_running=state['running']if state else None,world_result_satisfied=valid)
        outcome['ok']=outcome['ok']and valid
    if case.get('purpose_kind') == 'persistent_death':
        dead = any(e.get('dead') for e in result.get('plains', {}).get('enemies', []))
        outcome.update(required_world_result='enemy already dead, recovery still completes', enemy_dead=dead)
        outcome['ok'] = outcome['ok'] and dead
    return outcome


def checked_purpose(module, case, raw):
    result, interpretation = normalized(case, raw)
    check = module.purpose(case, result)
    check.setdefault('causal', {})['observer_interpretation'] = interpretation
    paired = any(l.get('paired_gate') for l in case.get('latches', []))
    violations = []
    if paired:
        for frame in raw.get('frames', []):
            state = frame.get('workshop', {}).get('paired_gates', [])
            if not state:
                violations.append(dict(frame=frame['frame'], reason='missing_actual_pair_state'))
            for gate in state:
                a, b = gate['open_a'], gate['open_b']
                exact = (a != b and gate['gate_a_layer'] == (0 if a else 1)
                         and gate['gate_b_layer'] == (0 if b else 1)
                         and gate['gate_a_disabled'] == a and gate['gate_b_disabled'] == b)
                if not exact:
                    violations.append(dict(frame=frame['frame'], reason='non_complementary_actual_collision'))
    check['causal']['paired_gate_invariant_violations'] = violations
    if violations:
        check['reasons'].append('actual_pair_collision_invariant_failed')
    check['ok'] = not check['reasons']
    return check


def counter_classification(case, raw, check, outcome, baseline=None):
    """Nominal causal demonstrations and legitimate route choices differ."""
    invalid = outcome['ok'] and not check['ok']
    reason = 'same external goal compared with original causal requirement'
    if outcome['ok'] and case.get('family') == 'finite-enemy-routes':
        causal = check['causal']
        safety={'player_harm','forbidden_ability','world_reset','actual_pair_collision_invariant_failed'}
        why=set(check['reasons'])
        if not why&safety and len(causal.get('staged_supports', [])) >= 2:
            invalid = False
            reason = 'allowed staged alternative: same reward, paid by real intermediate landings'
        elif not why&safety and causal.get('air_enemy_hits', 0) >= 2:
            invalid = False
            reason = 'allowed air alternative: same reward, paid by finite enemy hits'
    costs=None
    if baseline is not None:
        costs=dict(nominal={k:baseline.get(k)for k in ['shots','jumps','ticks']},alternative={k:raw.get(k)for k in ['shots','jumps','ticks']})
        paid_extra_action=raw.get('shots',0)>baseline.get('shots',0)or raw.get('jumps',0)>baseline.get('jumps',0)
        if invalid and case.get('required_carrier_park') and outcome['ok']and paid_extra_action and not set(check['reasons'])&{'player_harm','forbidden_ability','world_reset','actual_pair_collision_invariant_failed'}:
            invalid=False;reason='Allowed same-goal alternative pays extra real shot/jump actions; nominal causal demo retained, necessity not claimed'
    return dict(invalidates_design=invalid, reason=reason,cost_comparison=costs,
                same_external_outcome=outcome['ok'], reasonable_alternatives_preserved=True)


def preflight(engine, cases):
    static_preflight(engine, cases)
    # Reuse the original collected bundle, additionally map/validate the new
    # gate B. This is output validation, not a second physical implementation.
    subprocess.run(['node', str(HERE / 'export_v1.mjs'), str(engine.out / 'preflight-bundle.json'),
                    str(engine.out / 'batch-preflight-documents')], cwd=REPO, check=True, capture_output=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', required=True)
    parser.add_argument('--rules', required=True)
    parser.add_argument('--index', type=int, required=True, help='Predeclared relationship seed index')
    parser.add_argument('--interfaces', type=int, nargs='+', choices=[0, 1])
    args = parser.parse_args()
    authored = importlib.import_module(args.rules)
    rules = SimpleNamespace(__file__=authored.__file__, RECIPES=authored.RECIPES,
                            layouts=authored.layouts, alternatives=authored.alternatives,
                            purpose=lambda c, r: checked_purpose(authored, c, r))
    protocol_path = REPO / 'pcg/creative-production/batch30/protocol-v5.json'
    protocol = json.loads(protocol_path.read_text())
    if not 0 <= args.index < protocol['maximum_design_proposals']:
        raise ValueError('recipe seed index outside predeclared batch')
    config = dict(calibration_seed=protocol['calibration_seed'] + args.index * protocol['seed_stride'],
                  holdout_seed=protocol['holdout_seed'] + args.index * protocol['seed_stride'],
                  maximum_cases_per_proposal=protocol['maximum_full_cases_per_relationship'],
                  maximum_source_revisions=(8 if args.index==0 else 7) if args.index<2 else protocol['maximum_rule_revisions_per_proposal'])
    selected = [c for i in (args.interfaces or [0, 1]) for c in authored.layouts(authored.RECIPES[0], i)]
    paired = any(l.get('paired_gate') for c in selected for l in c.get('latches', []))
    dependencies = [Path(__file__), HERE / 'export_v1.mjs', protocol_path,
                    HERE.parent / 'junctions/landing_buffer_v1.py', HERE.parent / 'junctions/produce_v1.py']
    dependencies += [Path(p) for p in getattr(authored, 'SOURCE_DEPENDENCIES', [])]
    if paired:
        dependencies += [CELL / n for n in ['pair_latch_v1.gd', 'pair_latch_v2.gd','pair_latch_v3.gd', 'runtime_v3.gd',
                                            'runner_v3.gd', 'main_v3.gd', 'main_v3.tscn', 'protocol-v1.json']]
    runner = Path(authored.RUNNER_SCRIPT) if getattr(authored, 'RUNNER_SCRIPT', None) else (CELL / 'runner_v3.gd' if paired else None)
    run(args.name, interfaces=args.interfaces, recipe_module=rules,
        export_script=HERE / 'export_v1.mjs', protocol_config=config,
        extra_sources=dependencies, outcome_checker=external_outcome,
        runner_script=runner, preflight_fn=preflight, counter_classifier=counter_classification)


if __name__ == '__main__':
    main()
