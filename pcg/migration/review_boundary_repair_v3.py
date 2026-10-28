"""Append-only repair of one earned-return outbound exit fixture; no new holdout."""
from . import core

SCHEMA='pcg/review-boundary-fixture-repair/v3'

def validate_lineage(report,path):
    repair=report['boundaryRepair']
    if repair.get('schema')!=SCHEMA or repair.get('newIndependentHoldout')is not False or repair.get('newPhysicsAttempts')!=1:raise ValueError('invalid_boundary_repair_scope')
    core.verify_artifacts([repair[k]for k in ('sourceReport','repairBinding','repairBatches','repairChecks')])
    original=core.read(core.resolve_artifact(repair['sourceReport']['path']))
    allowed={'passed','actualAttempts','batches','probes','boundaryRepair'}
    if {k:v for k,v in original.items()if k not in allowed}!={k:v for k,v in report.items()if k not in allowed}:raise ValueError('boundary_repair_changed_original_routes_or_protocol')
    old=core.read(core.resolve_artifact(original['batches']['path']));new=core.read(core.resolve_artifact(report['batches']['path']));additional=core.read(core.resolve_artifact(repair['repairBatches']['path']))
    if new!=old+additional or sum(v['cases']for v in additional)!=1 or report['actualAttempts']!=original['actualAttempts']+1:raise ValueError('boundary_repair_attempt_lineage_mismatch')
    rows=core.read(core.resolve_artifact(repair['repairChecks']['path']))
    expected={'approved-first40-repair17-v2-A-to-C-migration-continuous-exit'}
    if {r['id']for r in rows}!=expected or len(rows)!=1 or not all(r['check']['passed']for r in rows):raise ValueError('boundary_repair_coverage_not_exact')
    before=core.read(core.resolve_artifact(original['probes']['path']));after=core.read(core.resolve_artifact(report['probes']['path']));byid={r['id']:r for r in rows}
    if after!=[byid.get(v['id'],v)for v in before]:raise ValueError('boundary_repair_altered_unrelated_probes')
    binding=core.read(core.resolve_artifact(repair['repairBinding']['path']));run=core.resolve_artifact(repair['repairBinding']['path']).parent
    previous_binding=core.read(core.resolve_artifact(original['sourceBinding']['path']))
    for key in ('engine_sha256','game_source_commit','source_index_sha256','protected_files','protected_mismatches'):
        if binding[key]!=previous_binding[key]:raise ValueError('boundary_repair_changed_engine_or_game')
    for rel,sha in previous_binding['source_files'].items():
        if rel not in ('migration/physics.py','migration/review_counter_scope_v2.py') and binding['source_files'].get(rel)!=sha:raise ValueError('boundary_repair_changed_original_runtime:'+rel)
    for rel,sha in binding['source_files'].items():
        if core.sha(run/'source_snapshot'/rel)!=sha:raise ValueError('boundary_repair_source_snapshot_changed')
