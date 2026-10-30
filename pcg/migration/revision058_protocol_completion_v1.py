"""Append-only completion of missing FULL probes; original calibration/holdout stay exact."""
from . import core
SCHEMA='pcg/review-protocol-completion/v1'
def validate_lineage(report,path):
 r=report['protocolCompletion'];assert r['schema']==SCHEMA and r['newIndependentHoldout']is False
 core.verify_artifacts([r[k]for k in ['sourceReport','supplementBinding','supplementBatches','supplementChecks','observer']])
 old=core.read(core.resolve_artifact(r['sourceReport']['path']));allowed={'passed','actualAttempts','batches','probes','protocol','counterexamples','protocolCompletion'}
 assert {k:v for k,v in old.items()if k not in allowed}=={k:v for k,v in report.items()if k not in allowed}
 before=core.read(core.resolve_artifact(old['protocol']['path']));after=core.read(core.resolve_artifact(report['protocol']['path']))
 from . import physics
 assert after==core.read(physics.FULL_PROTOCOL)
 for k in ['calibrationSeed','holdoutSeed','trialsPerNoiseLevel','thresholds','bodySize','boundaryVerticalOffsets','boundaryDirections']:assert before[k]==after[k]
 old_batches=core.read(core.resolve_artifact(old['batches']['path']));extra=core.read(core.resolve_artifact(r['supplementBatches']['path']));assert core.read(core.resolve_artifact(report['batches']['path']))==old_batches+extra
 assert r['newPhysicsAttempts']==sum(b['cases']for b in extra)<=32
 assert report['actualAttempts']==old['actualAttempts']+r['newPhysicsAttempts']
 assert all(b['stage']in ['full-v2-continuous-entry','full-v2-counters']for b in extra)
 before_probes=core.read(core.resolve_artifact(old['probes']['path']));now=core.read(core.resolve_artifact(report['probes']['path']));checks=core.read(core.resolve_artifact(r['supplementChecks']['path']))
 assert now[:len(before_probes)]==checks['originalProbesReobserved'] and now[len(before_probes):]==checks['newContinuousEntries']
 for a,b in zip(before_probes,checks['originalProbesReobserved']):
  assert {k:v for k,v in a.items()if k!='check'}=={k:v for k,v in b.items()if k!='check'}
  if a['check']!=b['check']:
   assert not a['check']['passed'] and b['check']['passed'] and b['check']['observationReanalysis']['kind']=='revision058_explicit_TOP_neighbor_caught_canonical_ascent'
 binding=core.read(core.resolve_artifact(r['supplementBinding']['path']));original_binding=core.read(core.resolve_artifact(old['sourceBinding']['path']))
 for k in ['engine_sha256','game_source_commit','source_index_sha256','protected_files','protected_mismatches']:assert binding[k]==original_binding[k]
 for k,sha in original_binding['source_files'].items():
  if k!='migration/physics.py':assert binding['source_files'].get(k)==sha
 return old
