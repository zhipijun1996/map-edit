"""Demand adaptation of an existing bell Module; at most eight real cases.

Only the oversized pit substrate and its attached thorn interval change. Main
supports, bell, gate, original forward action program and player tuning do not.
The new version receives new evidence; old pass records are never inherited.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re

from ..director import REPO, challenge_specs, design
from ..library import CandidateLibrary
from pcg.contract.export import export
from pcg.prototype.plains.engine import PlainsEngine
from pcg.prototype.plains.evaluation import instantiate, observed, purpose
from pcg.prototype.plains.synthesis import command, identity
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import POLICY, digest, gate, module_hash


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def bounds(case, omit_platform=None):
    rectangles = [p[:] for i, p in enumerate(case['platforms']) if i != omit_platform]
    rectangles += [p[:] for p in case.get('hazards', [])]
    source = REPO / 'pcg/prototype/godot/scripts/world/shot_latch.gd'
    match = re.search(r'bell_rectangle.size = Vector2\(([^,]+), ([^)]+)\)', source.read_text())
    if not match:
        raise ValueError('missing_original_bell_dimensions')
    bw, bh = map(float, match.groups())
    for latch in case.get('latches', []):
        rectangles.append(latch['gate'][:]); x, y = latch['bell']
        rectangles.append([x - bw / 2, y - bh / 2, bw, bh])
    low_x = min(p[0] for p in rectangles); high_x = max(p[0] + p[2] for p in rectangles)
    low_y = min(p[1] for p in rectangles); high_y = max(p[1] + p[3] for p in rectangles)
    return [low_x, low_y, high_x - low_x, high_y - low_y]


def adapt(parent, version, spec):
    case = copy.deepcopy(parent)
    if case['family'] != 'bell_lift' or case.get('saws') or case.get('enemies') or case.get('moving_platforms'):
        raise ValueError('unsupported_compact_adaptation_family')
    pit_indices = {int(t['platform_index']) for t in case.get('thorns', []) if t.get('surface_id') == 'pit_pressure'}
    if len(pit_indices) != 1:
        raise ValueError('requires_one_explicit_original_pit_pressure_host')
    pit = pit_indices.pop()
    if any(t['platform_index'] == pit and t.get('face') != 'top' for t in case['thorns']):
        raise ValueError('unsupported_pit_hazard_face')
    extent = bounds(case, omit_platform=pit)
    old_pit = case['platforms'][pit][:]
    left = extent[0] - 16
    right = extent[0] + extent[2] + 16
    case['platforms'][pit] = [left, old_pit[1], right - left, old_pit[3]]
    for thorn in case['thorns']:
        if thorn['platform_index'] == pit:
            thorn['start_offset'] = 0; thorn['length'] = right - left
    for key in ['factory_id', 'factory_evidence', 'module_sha256', 'recorded_frames', 'validation_summary',
                'review_alias', 'title', 'noise', 'map_demand', 'admission_status']:
        case.pop(key, None)
    extent = bounds(case)
    if extent[2] > spec['space']['max_width'] or extent[3] > spec['space']['max_height']:
        raise ValueError('compact_geometry_exceeds_requested_space')
    if abs(case['entry_port'][1] - case['exit_port'][1] - spec['rise']) > 1e-6:
        raise ValueError('compact_adaptation_changed_required_rise')
    case['world_bounds'] = extent[:]
    case['adaptation'] = {'method': 'crop_only_oversized_pit_substrate_to_real_cells_plus_16wu_each_side',
                          'parent_content_version': version, 'parent_case_sha256': module_hash(parent),
                          'parent_pit': old_pit, 'new_pit': case['platforms'][pit][:],
                          'unchanged': ['non_pit_platforms', 'bell', 'gate', 'forward_action_program', 'player_tuning'],
                          'request': copy.deepcopy(spec), 'inherited_physics_pass': False}
    case['id'] = 'compact-bell-' + identity(case)[:12]
    return case, extent


def reverse_cases(base):
    result = []
    plans = [
        ('walk-left', [command('settle', target_x=base['entry_port'][0], deadband=6)]),
        ('shoot-bell-then-left', [command('shoot', aim_cell={'kind': 'bell', 'id': 'lift_bell'}),
                                  command('settle', 6, target_x=base['entry_port'][0], deadband=6)]),
        ('jump-vertical-recoil-left', [command('axis', value=-1), command('jump'), command('jump_release', 12),
                                      command('shoot', 6, direction=[0, 1]),
                                      command('settle', 6, target_x=base['entry_port'][0], deadband=6)]),
        ('jump-diagonal-recoil-left', [command('axis', value=-1), command('jump'), command('jump_release', 12),
                                      command('shoot', 6, direction=[.25, .9682458365518543]),
                                      command('settle', 6, target_x=base['entry_port'][0], deadband=6)]),
    ]
    for name, plan in plans:
        case = copy.deepcopy(base)
        case['id'] += '-reverse-' + name
        case['spawn'] = base['exit_port'][:]; case['entry_port'] = case['spawn'][:]
        case['exit_port'] = base['entry_port'][:]
        case['entry_normal'] = base['exit_normal'][:]; case['exit_normal'] = base['entry_normal'][:]
        x, y = case['exit_port']; case['goal'] = [x - 24, y - 24, 48, 48]
        case['control_plan'] = plan; case['max_frames'] = 600
        case['reverse_attempt'] = name
        result.append(case)
    return result


def run(name='r2-compact-bell-v1'):
    out = REPO / 'pcg/results' / name
    if out.exists():
        raise ValueError('refuse_overwriting_compact_run')
    spec = challenge_specs(design())[1]
    spec.update(id='r2-room-compact-bell-100', objective='Fit an existing one-jump bell ascent into a real R2 room.')
    spec['space'] = {'max_width': 656, 'max_height': 624, 'max_port_span_x': 640}
    lookup = copy.deepcopy(spec); lookup['space']['max_width'] = 2000
    parents = CandidateLibrary().find(lookup)
    if not parents:
        raise ValueError('no_existing_verified_bell_lift_parent_for_adaptation')
    parent = parents[0]
    base, extent = adapt(parent['case'], parent['record']['contentVersion'], spec)
    engine = PlainsEngine(out, 8)
    source = Path(__file__)
    (out / 'compact-bell-source.py').write_bytes(source.read_bytes())
    protocol = {'schema': 'pcg/r2-compact-adaptation/v1', 'request': spec,
                'parent': {'record': parent['path'], 'contentVersion': parent['record']['contentVersion']},
                'source_sha256': file_sha(source), 'budget': 8,
                'selection': 'Use nominal forward trial regardless of perturbation outcomes; no geometry tuning or extra seed retries.',
                'policy': POLICY, 'regular_gate': '8-case budget insufficient for regular perturbation coverage; no automatic promotion',
                'reverse_scope': 'Independent original-exit fresh state only; no earned-state reverse guarantee',
                'physics_pass_inherited': False}
    write(out / 'protocol.json', protocol)
    nominal = copy.deepcopy(base); nominal['id'] += '-forward-nominal'
    delayed = copy.deepcopy(base); delayed['id'] += '-forward-settle-entry'
    delayed['control_plan'] = [command('wait', 8)] + delayed['control_plan']
    mild = instantiate(base, 241027103, 'mild', 0)
    moderate = instantiate(base, 241027103, 'moderate', 0)
    cases = [nominal, delayed, mild, moderate] + reverse_cases(base)
    write(out / 'requested-cases.json', {'cases': cases})
    rows = []; witness = None
    for index, (case, result, evidence) in enumerate(engine.run(cases, 'compact-forward-and-reverse')):
        forward = index < 4
        if forward:
            check = purpose(case, result)
        else:
            reasons = []
            if not result.get('ok'): reasons.append(result.get('reason', 'not_stable'))
            if result.get('hp') != 5 or result.get('returns') or result.get('plains', {}).get('player_damage'):
                reasons.append('harm_or_return')
            if any(result.get(k, 0) for k in ('air_jumps', 'grapples', 'wall_jumps')):
                reasons.append('forbidden_advanced_ability')
            check = {'ok': not reasons, 'reasons': reasons, 'behavior': observed(case, result)}
        rows.append({'case_id': case['id'], 'direction': 'forward' if forward else 'reverse',
                     'ok': check['ok'], 'reason': result['reason'], 'purpose': check,
                     'hp': result.get('hp'), 'ticks': result.get('ticks'), 'evidence': evidence,
                     'entry_snapshot': result.get('entry_snapshot'),
                     'exit_observation': result['frames'][-1] if result.get('frames') else None})
        if index == 0:
            witness = (case, result, evidence)
    write(out / 'route-results.json', rows)
    summary = {'schema': 'pcg/r2-compact-bell-result/v1', 'request': spec, 'bounds': extent,
               'entry_port': base['entry_port'], 'exit_port': base['exit_port'],
               'actual_physics_cases': engine.sim.cases, 'forward_passes': sum(r['ok'] for r in rows[:4]),
               'reverse_passes': sum(r['ok'] for r in rows[4:]), 'nominal_forward_pass': rows[0]['ok'],
               'human_fun': 'unverified', 'production_admitted': False,
               'regular_tier': 'unverified_insufficient_fresh_coverage',
               'candidate_status': 'passed_nominal_scoped' if rows[0]['ok'] else 'failed',
               'all_failures_retained': True}
    write(out / 'summary.json', summary)
    if not rows[0]['ok']:
        return summary
    case, result, evidence = witness
    case = copy.deepcopy(case); case['factory_id'] = identity(base); case['factory_evidence'] = evidence
    case['recorded_frames'] = [{'frame': f['frame'], 'axis': f['axis'], 'requested': f['requested']} for f in result['frames']]
    case['review_alias'] = case['title'] = 'R2紧凑钟台 · 原输入 / 新坑底版本'
    case['module_sha256'] = module_hash(case)
    cases_path = out / 'review_cases.json'; write(cases_path, {'cases': [case]})
    export(cases_path, out / 'modules', run=out)
    manifest = json.loads((out / 'modules/manifest.json').read_text())
    doc_path = out / 'modules' / manifest['modules'][0]['file']
    doc = json.loads(doc_path.read_text())
    destination = out / 'candidates' / doc['generationContract']['contentVersion'].removeprefix('sha256:')
    destination.mkdir(parents=True)
    write(destination / 'case.json', case)
    (destination / 'module.mapnote.json').write_bytes(doc_path.read_bytes())
    record = {'schema': 'map-notes/module-library-entry/v1', 'id': doc['id'],
              'contentVersion': doc['generationContract']['contentVersion'],
              'document_sha256': file_sha(destination / 'module.mapnote.json'),
              'case_sha256': file_sha(destination / 'case.json'),
              'technical_status': 'passed_nominal_scoped',
              'technical_scope': 'New compact forward nominal and listed fresh-entry attempts only; regular gate not met by sample budget.',
              'human_quality': 'awaiting_review', 'human_reviews': [], 'production_admitted': False,
              'quality_gate': {'status': 'insufficient_regular_coverage', 'required_policy': POLICY},
              'map_reuse_policy': 'explicit isolated placement and whole-map validation required; not returned by general CandidateLibrary.find',
              'evidence': [{'path': str(p.relative_to(REPO)), 'sha256': file_sha(p)} for p in
                           [out / 'route-results.json', out / 'source_binding.json', out / 'batches.json', out / 'protocol.json']]}
    write(destination / 'record.json', record)
    summary.update(candidate_record=str((destination / 'record.json').relative_to(REPO)),
                   canonical_document=str(doc_path.relative_to(REPO)), case=case)
    write(out / 'summary.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='r2-compact-bell-v1')
    args = parser.parse_args()
    summary = run(args.name)
    print(json.dumps({k: v for k, v in summary.items() if k != 'case'}, ensure_ascii=False, indent=2))
