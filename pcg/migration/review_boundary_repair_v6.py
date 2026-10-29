"""Append-only correction of 174's two below-one-way initialization probes."""
from . import core
SCHEMA='pcg/review-boundary-fixture-repair/v6'
def validate_lineage(report,path):
 r=report['boundaryRepair'];assert r['schema']==SCHEMA and r['newPhysicsAttempts']==2 and r['newIndependentHoldout']is False
 core.verify_artifacts([r[k]for k in ('sourceReport','repairBinding','repairBatches','repairChecks')]);old=core.read(core.resolve_artifact(r['sourceReport']['path']));allowed={'passed','actualAttempts','batches','probes','boundaryRepair'}
 if {k:v for k,v in old.items()if k not in allowed}!={k:v for k,v in report.items()if k not in allowed}:raise ValueError('oneway_repair_changed_nominal_evidence')
 before=core.read(core.resolve_artifact(old['probes']['path']));expected={p['id']for p in before if not p['check']['passed']};rows=core.read(core.resolve_artifact(r['repairChecks']['path']))
 assert len(expected)==2 and all('-174-'in i and '-exit-'in i and i.endswith('-2')for i in expected)
 assert {p['id']for p in rows}==expected and all(p['check']['passed']for p in rows)
 fixes={p['id']:p for p in rows};assert core.read(core.resolve_artifact(report['probes']['path']))==[fixes.get(p['id'],p)for p in before]
 additional=core.read(core.resolve_artifact(r['repairBatches']['path']));assert core.read(core.resolve_artifact(report['batches']['path']))==core.read(core.resolve_artifact(old['batches']['path']))+additional
 assert sum(p['cases']for p in additional)==2 and report['actualAttempts']==old['actualAttempts']+2
 binding=core.read(core.resolve_artifact(r['repairBinding']['path']));previous=core.read(core.resolve_artifact(old['sourceBinding']['path']));run=core.resolve_artifact(r['repairBinding']['path']).parent
 for k in ('engine_sha256','game_source_commit','source_index_sha256','protected_files','protected_mismatches'):assert binding[k]==previous[k]
 for p,sha in previous['source_files'].items():
  if p!='migration/physics.py':assert binding['source_files'].get(p)==sha
 for p,sha in binding['source_files'].items():assert core.sha(run/'source_snapshot'/p)==sha
