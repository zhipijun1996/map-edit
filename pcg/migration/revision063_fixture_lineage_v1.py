"""Validate appended ingress fixtures; never replace calibration or holdout."""
import copy
from . import core
SCHEMA='pcg/revision063-native-ingress-fixture-correction/v1'
def validate_lineage(report,path):
 r=report['fixtureCorrection'];assert r['schema']==SCHEMA and r['newIndependentHoldout']is False and r['newPhysicsAttempts']==4
 for key in ['sourceReport','sourceProbes','supplementBinding','supplementBatches','supplementChecks','builder']:core.verify_artifacts([r[key]])
 old=core.read(core.resolve_artifact(r['sourceReport']['path']));allowed={'passed','probes','batches','actualAttempts','fixtureCorrection'}
 assert {k:v for k,v in old.items()if k not in allowed}=={k:v for k,v in report.items()if k not in allowed}
 before=core.read(core.resolve_artifact(r['sourceProbes']['path']));after=core.read(core.resolve_artifact(report['probes']['path']));assert len(before)==len(after)
 changed=[]
 for a,b in zip(before,after):
  assert a['id']==b['id']
  if a!=b:
   assert not a['check']['passed'] and b['check']['passed'];changed.append(a['id'])
 assert len(changed)==4
 original_batches=core.read(core.resolve_artifact(old['batches']['path']));extra=core.read(core.resolve_artifact(r['supplementBatches']['path']))
 assert len(extra)==1 and extra[0]['stage']=='r063-fixture-repair' and extra[0]['cases']==4
 assert core.read(core.resolve_artifact(report['batches']['path']))==original_batches+extra and report['actualAttempts']==old['actualAttempts']+4
 a=core.read(core.resolve_artifact(old['sourceBinding']['path']));b=core.read(core.resolve_artifact(r['supplementBinding']['path']))
 for key in ['engine_sha256','game_source_commit','source_index_sha256','protected_files','protected_mismatches','runner']:assert a[key]==b[key]
 for key,sha in a['source_files'].items():
  if key!='migration/physics.py':assert b['source_files'].get(key)==sha
 checks=core.read(core.resolve_artifact(r['supplementChecks']['path']));assert checks['passed'] and checks['replacedProbeIds']==changed and checks['canonicalProgramsChanged']is False
 from .revision063_fixture_v2 import adjust
 for row in checks['rows']:
  core.verify_artifacts([row['originalInput'],row['correctedInput']]);oldcase=core.read(core.resolve_artifact(row['originalInput']['path']))['cases'][row['originalIndex']];newcase=core.read(core.resolve_artifact(row['correctedInput']['path']))['cases'][row['correctedIndex']]
  expected=copy.deepcopy(oldcase);assert adjust(expected)
  from .physics import module_hash
  expected['module_sha256']=module_hash(expected);assert expected==newcase
 return old
