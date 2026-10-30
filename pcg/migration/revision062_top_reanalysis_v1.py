"""Validate append-only read-only boundary-observation correction provenance."""
from . import core
SCHEMA='pcg/revision062-native-neighbor-observation-correction/v1'
def validate_lineage(report,path):
 r=report['boundaryObservationCorrection'];assert r['schema']==SCHEMA and r['newPhysicsAttempts']==0 and r['newIndependentHoldout']is False;core.verify_artifacts([r[k]for k in ['sourceReport','sourceProbes','observer','originalObserver','nativePropertyProbe','analysis']]);old=core.read(core.resolve_artifact(r['sourceReport']['path']));allowed={'passed','probes','boundaryObservationCorrection'};assert {k:v for k,v in old.items()if k not in allowed}=={k:v for k,v in report.items()if k not in allowed};before=core.read(core.resolve_artifact(r['sourceProbes']['path']));after=core.read(core.resolve_artifact(report['probes']['path']));assert len(before)==len(after)
 for a,b in zip(before,after):
  assert {k:v for k,v in a.items()if k!='check'}=={k:v for k,v in b.items()if k!='check'}
  if a['check']!=b['check']:
   assert not a['check']['passed']and b['check']['passed'];proof=b['check']['observationReanalysis'];assert proof['kind']=='revision062_native_neighbor_contact_within_original_safe_margin'and proof['requiresActualNeighborSupportId'];assert all(b['check'][k]for k in ['bodyPassedBothSides','requiredWorldOutcomeSatisfied','directionOrdered','healthy','noReset']);assert not b['check']['apertureViolationFrames']
 if r.get('reservedExecutionAlias'):
  core.verify_artifacts([r['reservedExecutionAlias']]);alias=core.read(core.resolve_artifact(r['reservedExecutionAlias']['path']));assert alias['sameCandidate']and alias['sameProtocolPoolSeeds']and alias['newPhysicsAttempts']==0 and path.parent.name==alias['originalReservedExperiment']
  for row in alias['links']:
   target=core.REPO/row['aliasPath'];assert target.is_symlink()and target.readlink().as_posix()==row['symlink'];core.verify_artifacts([row['source']]);assert core.sha(target)==row['source']['sha256']
 return old
