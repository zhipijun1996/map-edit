"""Finite Map-demand adapter for the existing plains Module generator.

It does not replace motion synthesis, physics, output contracts or quality gates.
The narrow first implementation supports two-port, enemy-free bell ascents.
"""
from __future__ import annotations

import copy
import hashlib
import json
import math
from pathlib import Path
import re

from ..prototype.plains import synthesis
from ..prototype.plains.evaluation import instantiate, observed, purpose
from ..prototype.plains.produce import alternative_cases
from ..prototype.factory.core.quality import (
    BehaviorArchive, POLICY, counts, digest, discovery_quality, gate, module_hash,
)


def _write(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def _finite(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def _space(spec):
    return spec.get('space', spec)


def _capabilities(spec):
    requirements = spec.get('capabilities', {})
    if not isinstance(requirements, dict) or requirements.get('status') != 'defined' or requirements.get('anyOfGroups'):
        return None
    return requirements.get('allOf')


def _spec_errors(spec):
    errors = []
    ports = spec.get('ports', {})
    if not isinstance(ports, dict) or ports.get('count') != 2:
        errors.append({'condition': 'ports', 'reason': 'supported_port_count_is_two'})
    if isinstance(ports, dict) and ports.get('required_normals') != [[-1, 0], [1, 0]]:
        errors.append({'condition': 'ports.required_normals', 'reason': 'supports_declared_west_entry_east_exit_only'})
    if _capabilities(spec) != ['move', 'jump', 'shot_recoil']:
        errors.append({'condition': 'capabilities', 'reason': 'requires_exact_existing_plains_capabilities'})
    if spec.get('required_family') != 'bell_lift':
        errors.append({'condition': 'required_family', 'reason': 'supported_family_is_bell_lift'})
    if spec.get('entry_y') != 420:
        errors.append({'condition': 'entry_y', 'reason': 'existing_probe_entry_y_is_420'})
    if not _finite(spec.get('rise')) or not 0 < spec['rise'] < 420:
        errors.append({'condition': 'rise', 'reason': 'requires_finite_positive_ascent_below_420'})
    if spec.get('require_bell') is not True:
        errors.append({'condition': 'require_bell', 'reason': 'this_adapter_supports_bell_ascent_only'})
    for key in ('max_width', 'max_height', 'max_port_span_x'):
        value = _space(spec).get(key)
        if value is not None and (not _finite(value) or value <= 0):
            errors.append({'condition': 'space.' + key, 'reason': 'requires_finite_positive_budget'})
    if _space(spec).get('max_width') is None:
        errors.append({'condition': 'space.max_width', 'reason': 'explicit_real_occupancy_budget_required'})
    return errors


def _bounds(case, engine):
    """Known solid/hazard/bell envelopes; not a universal action-clearance proof."""
    rectangles = [list(r) for r in case.get('platforms', []) + case.get('hazards', [])]
    if any(case.get(k) for k in ('saws', 'moving_platforms', 'hooks', 'enemies')):
        raise ValueError('unsupported_geometry_envelope')
    # Read the actual protected ShotLatch dimensions rather than creating a
    # second numeric default. These candidates use only top-facing pit thorns.
    source = engine.out / 'source_snapshot/prototype/godot/scripts/world/shot_latch.gd'
    match = re.search(r'bell_rectangle.size = Vector2\(([^,]+), ([^)]+)\)', source.read_text())
    if not match:
        raise ValueError('unbound_bell_dimensions')
    bell_width, bell_height = map(float, match.groups())
    for latch in case.get('latches', []):
        rectangles.append(latch['gate'][:])
        x, y = latch['bell']
        rectangles.append([x - bell_width / 2, y - bell_height / 2, bell_width, bell_height])
    for thorn in case.get('thorns', []):
        if thorn.get('face') != 'top':
            raise ValueError('unsupported_thorn_envelope')
        platform = case['platforms'][thorn['platform_index']]
        rectangles.append([platform[0] + thorn['start_offset'], platform[1] - thorn['depth'],
                           thorn['length'], thorn['depth']])
    left = min(r[0] for r in rectangles)
    top = min(r[1] for r in rectangles)
    right = max(r[0] + r[2] for r in rectangles)
    bottom = max(r[1] + r[3] for r in rectangles)
    return [left, top, right - left, bottom - top]


def _geometry_errors(case, spec, engine):
    try:
        bounds = _bounds(case, engine)
    except ValueError as error:
        return [{'condition': 'space', 'reason': str(error)}], None
    errors = []
    if bounds[2] > _space(spec)['max_width']:
        errors.append({'condition': 'space.max_width', 'reason': 'spatial_width_exceeds_max',
                       'required': bounds[2], 'available': _space(spec)['max_width']})
    maximum_height = _space(spec).get('max_height')
    if maximum_height is not None and bounds[3] > maximum_height:
        errors.append({'condition': 'space.max_height', 'reason': 'spatial_height_exceeds_max',
                       'required': bounds[3], 'available': maximum_height})
    span = abs(case['exit_port'][0] - case['entry_port'][0])
    maximum = _space(spec).get('max_port_span_x')
    if maximum is not None and span > maximum:
        errors.append({'condition': 'space.max_port_span_x', 'reason': 'port_span_exceeds_max',
                       'required': span, 'available': maximum})
    actual_rise = case['entry_port'][1] - case['exit_port'][1]
    if abs(actual_rise - spec['rise']) > 1e-6:
        errors.append({'condition': 'rise', 'reason': 'wrong_port_height', 'actual': actual_rise})
    return errors, bounds


def fill(spec, engine):
    """Return technical_candidate or structured unsatisfied; never approve fun.

    spec: canonical map-notes/challenge-specification/v1, ports.count=2,
    capabilities in the existing requirement format, entry_y=420, rise,
    require_bell=True, space.max_width / max_height / max_port_span_x.
    engine: existing PlainsEngine. All calls retain its input/output/source log.
    """
    request = copy.deepcopy(spec)
    request_id = digest(request)[:16]
    out = engine.out / 'demand_fill' / request_id
    if out.exists():
        raise ValueError('Refuse overwriting demand fill evidence: ' + str(out))
    out.mkdir(parents=True)
    adapter_source = Path(__file__).read_bytes()
    (out / 'fill-source.py').write_bytes(adapter_source)
    calibration_seed, holdout_seed = 241025101, 241025903
    protocol = {
        'schema': 'pcg/map-demand-fill/v1', 'request': request, 'request_sha256': digest(request),
        'adapter_source_sha256': hashlib.sha256(adapter_source).hexdigest(),
        'producer': 'existing plains.synthesis.proposals/materialize',
        'budgets': {'motion_probes': 8, 'geometry_candidates': 8, 'calibration_levels': ['clean', 'mild'],
                    'calibration_trials_per_level': 1,
                    'holdout_trials': {'clean': 1, 'mild': 12, 'moderate': 12},
                    'counterfactual_trials': 4, 'holdout_attempts': 1},
        'calibration_seed': calibration_seed, 'holdout_seed': holdout_seed,
        'selection': 'existing BehaviorArchive, executed sequence and requested rise bin; highest discovery quality then content identity before holdout',
        'policy': copy.deepcopy(POLICY),
        'scope': 'finite automated policy; no general seam/transform/state-transfer, human-fun or production admission',
    }
    _write(out / 'protocol.json', protocol)
    failures = []

    def stop(reason, unsatisfied):
        result = {'status': 'unsatisfied', 'reason': reason, 'unsatisfied': unsatisfied,
                  'failures': failures, 'request_sha256': digest(request), 'protocol': protocol,
                  'evidence_directory': str(out), 'human_quality': 'unverified', 'production_admitted': False}
        _write(out / 'result.json', result)
        return result

    errors = _spec_errors(spec)
    if errors:
        return stop('unsupported_challenge_specification', errors)

    probes = [p for p in synthesis.proposals() if p['family'] == 'bell_lift'][:8]
    candidates = []
    for case, result, evidence in engine.run(probes, 'demand-motion-' + request_id):
        materialized = synthesis.materialize(case, result, heights=[spec['entry_y'] - spec['rise']])
        if not materialized:
            failures.append({'stage': 'motion_materialization', 'case_id': case['id'],
                             'reason': 'no_measured_landing_for_requested_height', 'evidence': evidence})
        for candidate in materialized:
            candidate['entry_normal'] = [-1, 0]
            candidate['exit_normal'] = [1, 0]
            candidate['map_demand'] = {'request_sha256': digest(request), 'request': request,
                                       'adapter_source_sha256': protocol['adapter_source_sha256']}
            issues, bounds = _geometry_errors(candidate, spec, engine)
            if issues:
                failures.append({'stage': 'geometry_budget', 'case_id': candidate['id'],
                                 'unsatisfied': issues, 'bounds': bounds, 'evidence': evidence})
                continue
            candidates.append(candidate)
    candidates = sorted({synthesis.identity(c): c for c in candidates}.values(), key=synthesis.identity)[:8]
    _write(out / 'geometry_candidates.json', {'cases': candidates, 'failures': failures})
    if not candidates:
        unsatisfied = [issue for row in failures for issue in row.get('unsatisfied', [])]
        return stop('no_candidate_satisfies_requested_geometry', unsatisfied or [
            {'condition': 'rise', 'reason': 'no_measured_landing_in_bounded_probe_domain'}])

    archive = BehaviorArchive()
    calibrated = {}
    calibration_cases = [instantiate(c, calibration_seed, 'clean', 0) for c in candidates]
    owners = {c['id'] + '-clean-0': c for c in candidates}
    for case, result, evidence in engine.run(calibration_cases, 'demand-calibration-' + request_id):
        base = owners[case['id']]
        check = purpose(case, result)
        stats = counts([{'purpose': check, 'safe_stable': bool(result.get('ok'))}])
        behavior = observed(case, result)
        # No mild evidence is invented: reuse the clean observation as the
        # explicit discovery statistic for this narrow preselection only.
        discovery = {'clean': stats, 'mild': dict(trials=0, purpose_valid=0, safe_stable=0, rate=0, wilson95=[0, 1])}
        features = {'cell': [behavior['signature'], int(spec['rise'] // 40)],
                    'stationary_fraction': sum(abs(f.get('real_velocity', [f.get('vx', 0), 0])[0]) < 2
                                               for f in result.get('frames', [])) / max(1, len(result.get('frames', []))),
                    'source': 'actual executed action sequence and port rise bin'}
        entry = {'uid': synthesis.identity(base), 'case': base, 'features': features,
                 'discovery': discovery, 'quality': discovery_quality(discovery, features),
                 'violation': int(not check['ok']), 'evidence': evidence, 'purpose': check,
                 'behavior': behavior}
        archive.insert(entry)
        calibrated[entry['uid']] = entry
        if not check['ok']:
            failures.append({'stage': 'calibration', 'case_id': case['id'], 'reason': check['reasons'], 'evidence': evidence})
    # BehaviorArchive requires a real mild discovery sample to populate its
    # feasible archive. Evaluate one per candidate rather than pretending the
    # clean run measured mild perturbations.
    mild_cases = [instantiate(c, calibration_seed, 'mild', 0) for c in candidates]
    owners = {c['id'] + '-mild-0': c for c in candidates}
    for case, result, evidence in engine.run(mild_cases, 'demand-mild-calibration-' + request_id):
        entry = calibrated[synthesis.identity(owners[case['id']])]
        check = purpose(case, result)
        entry['discovery']['mild'] = counts([{'purpose': check, 'safe_stable': bool(result.get('ok'))}])
        entry['quality'] = discovery_quality(entry['discovery'], entry['features'])
        entry['violation'] += int(not check['ok'])
        archive.insert(entry)
        if not check['ok']:
            failures.append({'stage': 'mild_calibration', 'case_id': case['id'], 'reason': check['reasons'], 'evidence': evidence})
    protocol['archive_history'] = archive.history
    protocol['feasible_behavior_cells'] = len(archive.feasible)
    protocol['infeasible_behavior_cells'] = len(archive.infeasible)
    _write(out / 'protocol.json', protocol)
    _write(out / 'calibration.json', list(calibrated.values()))
    if not archive.feasible:
        return stop('calibration_failed', [{'condition': 'technical_quality', 'reason': 'no_clean_and_mild_discovery_candidate'}])
    selected = sorted(archive.feasible.values(), key=lambda e: (-e['quality'], e['uid']))[0]
    base = selected['case']
    protocol['selected_before_holdout'] = selected['uid']
    _write(out / 'protocol.json', protocol)

    held_rows = []
    witness = None
    for level in ('clean', 'mild', 'moderate'):
        # Static clean geometry is deterministic: the existing policy requires
        # one nominal trial. Twelve identical copies would not add coverage.
        trials = 1 if level == 'clean' and not base.get('saws') and not base.get('enemies') else 12
        cases = [instantiate(base, holdout_seed, level, trial) for trial in range(trials)]
        for case, result, evidence in engine.run(cases, 'demand-holdout-' + level + '-' + request_id):
            check = purpose(case, result)
            row = {'level': level, 'purpose': check, 'safe_stable': bool(result.get('ok')),
                   'evidence': evidence, 'case_id': case['id']}
            held_rows.append(row)
            if level == 'clean':
                witness = {'case': case, 'result': result, 'evidence': evidence}
            if not check['ok']:
                failures.append({'stage': 'holdout', 'case_id': case['id'], 'reason': check['reasons'], 'evidence': evidence})
    stats = {level: counts([r for r in held_rows if r['level'] == level]) for level in ('clean', 'mild', 'moderate')}
    counterfactuals = []
    alternatives = []
    owners = {}
    for kind, alternative in alternative_cases(base):
        if kind not in ('no_shoot', 'no_shoot_held_jump', 'wrong_aim'):
            continue
        for trial in range(4):
            case = instantiate(alternative, holdout_seed, 'clean', trial)
            alternatives.append(case)
            owners[case['id']] = kind
    shortcuts = []
    for case, result, evidence in engine.run(alternatives, 'demand-counterfactual-' + request_id):
        physical = bool(result.get('ok') and result.get('hp') == 5 and not result.get('plains', {}).get('player_damage'))
        row = {'kind': owners[case['id']], 'case_id': case['id'], 'physical_pass': physical,
               'reason': result.get('reason'), 'evidence': evidence}
        counterfactuals.append(row)
        if physical and row['kind'] in ('no_shoot', 'no_shoot_held_jump'):
            shortcuts.append(row)
    quality = gate(stats, shortcuts, bool(base.get('saws') or base.get('enemies')), POLICY, requested_tier='regular')
    _write(out / 'holdout.json', {'rows': held_rows, 'stats': stats, 'counterfactuals': counterfactuals, 'quality': quality})
    if quality['status'] != 'awaiting_human_review' or not witness or not purpose(witness['case'], witness['result'])['ok']:
        return stop('independent_holdout_failed', [{'condition': 'technical_quality', 'reason': quality['reasons']}])
    case = copy.deepcopy(witness['case'])
    case['factory_id'] = selected['uid']
    case['factory_evidence'] = witness['evidence']
    case['validation_summary'] = stats
    case['recorded_frames'] = [{'frame': f['frame'], 'axis': f['axis'], 'requested': f['requested']}
                               for f in witness['result']['frames']]
    case['title'] = case['review_alias'] = 'Map需求补缺：100wu钟台' if spec['rise'] == 100 else 'Map需求补缺：钟台'
    case['module_sha256'] = module_hash(case)
    result = {'status': 'technical_candidate', 'case': case, 'evidence': witness['evidence'],
              'quality': quality, 'stats': stats, 'behavior': selected['behavior'],
              'bounds': _bounds(case, engine), 'failures': failures, 'protocol': protocol,
              'request_sha256': digest(request), 'evidence_directory': str(out),
              'human_quality': 'unverified', 'production_admitted': False,
              'scope': 'candidate only; automatic interface and whole-map passage require separate validation'}
    _write(out / 'review_cases.json', {'cases': [case]})
    _write(out / 'result.json', result)
    return result
