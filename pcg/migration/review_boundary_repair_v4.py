"""Append-only correction of malformed continuous-exit test fixtures."""
from . import core
SCHEMA='pcg/review-boundary-fixture-repair/v4'
def validate_lineage(report,path):
 r=report['boundaryRepair']
 if r.get('schema')!=SCHEMA or r.get('newIndependentHoldout')is not False:raise ValueError('invalid_boundary_repair_scope')
 core.verify_artifacts([r[k]for k in ('sourceReport','repairBinding','repairBatches','repairChecks')]);old=core.read(core.resolve_artifact(r['sourceReport']['path']));allowed={'passed','actualAttempts','batches','probes','boundaryRepair'}
 if {k:v for k,v in old.items()if k not in allowed}!={k:v for k,v in report.items()if k not in allowed}:raise ValueError('boundary_repair_changed_original_routes_or_protocol')
 before=core.read(core.resolve_artifact(old['probes']['path']));failed={v['id']for v in before if not v['check']['passed']};rows=core.read(core.resolve_artifact(r['repairChecks']['path']));count=len(failed)
 if count not in (1,2,7)or r.get('newPhysicsAttempts')!=count or {v['id']for v in rows}!=failed or len(rows)!=count or not all(v['check']['passed']for v in rows):raise ValueError('boundary_repair_not_exact_failed_fixture_coverage')
 if not all('-125-'in v or '-140-'in v or '-150-'in v or '-154-'in v for v in failed):raise ValueError('boundary_repair_design_scope_changed')
 additional=core.read(core.resolve_artifact(r['repairBatches']['path']));batches=core.read(core.resolve_artifact(report['batches']['path']))
 if batches!=core.read(core.resolve_artifact(old['batches']['path']))+additional or sum(v['cases']for v in additional)!=count or report['actualAttempts']!=old['actualAttempts']+count:raise ValueError('boundary_repair_attempt_lineage_mismatch')
 fixes={v['id']:v for v in rows}
 if core.read(core.resolve_artifact(report['probes']['path']))!=[fixes.get(v['id'],v)for v in before]:raise ValueError('boundary_repair_altered_unrelated_probes')
 binding=core.read(core.resolve_artifact(r['repairBinding']['path']));previous=core.read(core.resolve_artifact(old['sourceBinding']['path']));run=core.resolve_artifact(r['repairBinding']['path']).parent
 for k in ('engine_sha256','game_source_commit','source_index_sha256','protected_files','protected_mismatches'):
  if binding[k]!=previous[k]:raise ValueError('boundary_repair_changed_engine_or_game')
 for rel,sha in previous['source_files'].items():
  if rel!='migration/physics.py'and binding['source_files'].get(rel)!=sha:raise ValueError('boundary_repair_changed_original_runtime:'+rel)
 for rel,sha in binding['source_files'].items():
  if core.sha(run/'source_snapshot'/rel)!=sha:raise ValueError('boundary_repair_source_snapshot_changed')
