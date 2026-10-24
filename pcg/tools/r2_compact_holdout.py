"""Independent fixed-candidate compact-bell holdout; no search or geometry repair."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
import shutil
import sys

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from pcg.contract.export import export
from pcg.map_directed.library import CandidateLibrary
from pcg.prototype.plains.engine import PlainsEngine
from pcg.prototype.plains.evaluation import instantiate, purpose
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import POLICY, counts, digest, gate, module_hash


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + '\n')


def run(name='r2-compact-bell-holdout-v1', source='r2-compact-bell-v1'):
    source_dir = REPO / 'pcg/results' / source
    source_cases = source_dir / 'requested-cases.json'
    original = json.loads(source_cases.read_text())['cases'][0]
    source_review = json.loads((source_dir / 'review_cases.json').read_text())['cases'][0]
    summary_source = json.loads((source_dir / 'summary.json').read_text())
    if not summary_source['nominal_forward_pass'] or original['id'] != source_review['id']:
        raise ValueError('selected_nominal_candidate_not_identifiable')
    # Compare all raw input fields to the independently exported original
    # witness before creating any new physics run. Extra review labels and
    # evidence cannot replace a geometry/action-program binding.
    for key, value in original.items():
        if source_review.get(key) != value:
            raise ValueError('source_nominal_input_drift/' + key)
    if module_hash(source_review) != source_review['module_sha256']:
        raise ValueError('source_compact_review_hash_drift')
    out = REPO / 'pcg/results' / name
    if out.exists():
        raise ValueError('immutable_holdout_run_exists')
    out.mkdir(parents=True)
    seed = 241024991
    geometry_keys = ('capabilities', 'platforms', 'one_way_platform_indices', 'wall_platform_indices',
                     'hazards', 'thorns', 'saws', 'moving_platforms', 'hooks', 'latches', 'enemies',
                     'world_bounds', 'entry_port', 'exit_port', 'spawn', 'goal')
    geometry_sha = digest({k: original.get(k) for k in geometry_keys})
    protocol = {'schema': 'pcg/r2-compact-fixed-holdout/v1', 'seed': seed,
                'selected_case_id': original['id'], 'selected_factory_id': source_review['factory_id'],
                'selected_geometry_sha256': geometry_sha,
                'source_input': {'path': str(source_cases.relative_to(REPO)), 'sha256': file_sha(source_cases)},
                'source_review': {'path': str((source_dir / 'review_cases.json').relative_to(REPO)),
                                  'sha256': file_sha(source_dir / 'review_cases.json')},
                'request': summary_source['request'], 'policy': copy.deepcopy(POLICY),
                'trial_counts': {'clean': 1, 'mild': 12, 'moderate': 12}, 'total_cases': 25,
                'selection': 'The original nominal candidate is fixed before this new independent holdout. No replacement, repair, alternate seed or reclassification after any failure.',
                'counterfactual_scope': 'No new alternative-policy search in this fixed 25-case budget; empty shortcut list means no observed new shortcut, not a necessity proof.',
                'reverse_scope': 'This holdout covers the forward entry→exit only. Earlier reverse attempts remain separately scoped.',
                'source_sha256': file_sha(Path(__file__)),
                'human_fun': 'unverified', 'production_admitted': False}
    write(out / 'protocol.json', protocol)
    # Engine refuses existing directories, so create it in its own immutable
    # subdirectory; protocol is recorded before any physical evaluation.
    engine = PlainsEngine(out / 'physics-run', 12)
    rel = Path(__file__).relative_to(REPO / 'pcg').as_posix()
    engine.hashes[rel] = file_sha(Path(__file__))
    snapshot = engine.out / 'source_snapshot' / rel
    snapshot.parent.mkdir(parents=True, exist_ok=True); shutil.copy2(__file__, snapshot)
    engine.binding['source_files'] = engine.hashes
    engine.binding['source_manifest_sha256'] = digest(engine.hashes)
    write(engine.out / 'source_binding.json', engine.binding)
    write(engine.out / 'protocol.json', protocol)
    cases = []; owners = {}
    for level, trials in protocol['trial_counts'].items():
        for trial in range(trials):
            case = instantiate(original, seed, level, trial)
            if digest({k: case.get(k) for k in geometry_keys}) != geometry_sha:
                raise ValueError('holdout_changed_fixed_geometry')
            cases.append(case); owners[case['id']] = (level, trial)
    rows = []; witness = None
    for case, result, evidence in engine.run(cases, 'independent-fixed-compact-bell'):
        level, trial = owners[case['id']]
        check = purpose(case, result)
        rows.append({'case_id': case['id'], 'level': level, 'trial': trial,
                     'purpose': check, 'safe_stable': bool(result.get('ok')),
                     'reason': result['reason'], 'hp': result.get('hp'), 'ticks': result.get('ticks'),
                     'evidence': evidence})
        if level == 'clean':
            witness = (copy.deepcopy(case), result, evidence)
    stats = {level: counts([r for r in rows if r['level'] == level]) for level in protocol['trial_counts']}
    quality = gate(stats, [], bool(original.get('saws') or original.get('enemies')), POLICY,
                   requested_tier='regular')
    write(out / 'results.json', {'rows': rows, 'stats': stats, 'quality': quality})
    summary = {'schema': 'pcg/r2-compact-holdout-result/v1', 'source': source,
               'seed': seed, 'fixed_geometry_sha256': geometry_sha,
               'actual_physics_cases': engine.sim.cases, 'stats': stats, 'quality': quality,
               'human_fun': 'unverified', 'production_admitted': False,
               'candidate_enrolled': False, 'new_alternative_policy_search': False,
               'all_failures_retained': True}
    write(out / 'summary.json', summary)
    if quality['status'] != 'awaiting_human_review' or witness is None or not purpose(witness[0], witness[1])['ok']:
        return summary
    case, result, evidence = witness
    case['factory_id'] = source_review['factory_id']
    case['factory_evidence'] = evidence
    case['validation_summary'] = stats
    case['recorded_frames'] = [{'frame': f['frame'], 'axis': f['axis'], 'requested': f['requested']} for f in result['frames']]
    case['review_alias'] = case['title'] = 'R2紧凑钟台 · 固定版本独立留出'
    case['module_sha256'] = module_hash(case)
    review = out / 'review_cases.json'; write(review, {'cases': [case]})
    # Preserve the original fixed run binding expected by the existing exporter.
    export(review, out / 'modules', run=engine.out)
    manifest = json.loads((out / 'modules/manifest.json').read_text())
    document_path = out / 'modules' / manifest['modules'][0]['file']
    artifacts = [{'path': str(p.relative_to(REPO)), 'sha256': file_sha(p)} for p in
                 [out / 'protocol.json', out / 'results.json', engine.out / 'source_binding.json',
                  engine.out / 'batches.json', document_path]]
    library = CandidateLibrary()
    record = library.enroll(case, document_path, quality, artifacts)
    matches = CandidateLibrary().find(summary_source['request'])
    matched = [m for m in matches if m['record']['contentVersion'] == record['contentVersion']]
    if not matched:
        raise ValueError('enrolled_compact_candidate_not_found_by_same_space_requirement')
    summary.update(candidate_enrolled=True, candidate_id=record['id'], contentVersion=record['contentVersion'],
                   canonical_document=str(document_path.relative_to(REPO)),
                   candidate_record=matched[0]['path'], same_requirement_requery_matches=len(matched),
                   production_rejections=CandidateLibrary.promotion_reasons(record),
                   generic_assembly_admitted=False)
    write(out / 'summary.json', summary)
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--name', default='r2-compact-bell-holdout-v1')
    parser.add_argument('--source', default='r2-compact-bell-v1')
    args = parser.parse_args()
    print(json.dumps(run(args.name, args.source), ensure_ascii=False, indent=2))
