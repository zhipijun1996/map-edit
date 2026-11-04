"""Keep formal failures and deliver input repairs derived only from calibration."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,sys
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .continue_revision063_v1 import rows,label,OUT
from . import finalize_revision063_v1 as final
VERSIONS={'s04':'repair-v8','s09':'repair-v9'}
def run(row):
 n=label(row);original=final.FINAL/row['moduleId'];failed=core.read(original/'qualification.json');assert failed['passed']is False
 final.ROOT=core.REPO/'pcg/manual_review/implementation/revision-063-repaired-samples-v1';final.freeze(row,VERSIONS[n],demo=True);sample=final.folder_for(row);templates={c['route_spec']['id']:c for c in core.read(sample/'physics-input-cases.json')['cases']};report_path=core.resolve_artifact(failed['report']['path']);report=core.read(report_path);inputs=[];lineage=[];counts={}
 for route in report['routes']:
  cal=core.read(core.resolve_artifact(route['calibration']['path']))
  for before in cal['rows']:
   if before['purpose']['ok']:continue
   e=before['evidence'];p=report_path.parent/'physics'/(e['batch']+'.input.json');old=core.read(p)['cases'][e['index']];new=copy.deepcopy(old);template=templates[route['routeId']];new['control_plan']=copy.deepcopy(template['control_plan']);new['generation_rule']=copy.deepcopy(template['generation_rule']);new['id']+='-r063-repair-replay';new['module_sha256']=physics.module_hash(new);inputs.append(new)
   ignored={'id','control_plan','generation_rule','module_sha256'};assert {k:v for k,v in old.items()if k not in ignored}=={k:v for k,v in new.items()if k not in ignored}
   lineage.append(dict(route=route['routeId'],originalInput=physics.artifact(p),originalIndex=e['index'],samePhysicalConditionsAndNoise=True,originalFailure=before['purpose']));counts[route['routeId']]=counts.get(route['routeId'],0)+1
 assert inputs and all(v+1<=18 for v in counts.values())
 eng,cs,authors=physics._engine(sample,'approved-r063-'+n+'-known-calibration-repair-'+VERSIONS[n],physics.FULL_PROTOCOL);checks=[]
 for c,raw,e in eng.run(inputs,'same-calibration-input-repair'):
  q=checked_purpose(physics.author_for(c),c,raw);checks.append(dict(route=c['route_spec']['id'],check=q,evidence=e));print(n,'KNOWN_CALIBRATION_REPAIR',q['ok'],q['reasons'],flush=True)
 passed=all(q['check']['ok']for q in checks);core.write(eng.out/'repair-check.json',dict(passed=passed,rows=checks,lineage=lineage,originalFormalFailureRetained=failed['report'],newIndependentHoldout=False,diagnosticsPerRouteVersion={k:v+1 for k,v in counts.items()},screenBudgetSeparate=True))
 q=core.read(sample/'qualification.json');q.update(status='REPAIRED_SAMPLE_FORMAL_PENDING'if passed else'REPAIRED_SAMPLE_CALIBRATION_STILL_PARTIAL',priorFailedQualification=failed,knownCalibrationFailuresRepaired=physics.artifact(eng.out/'repair-check.json'),knownCalibrationRepairPassed=passed,reason='Native sample is updated using calibration only. The selected formal failure remains immutable; no second formal candidate or holdout pool was allocated.');core.write(sample/'qualification.json',q);final.deliver(row)
 p=OUT/'delivery-selection.json';mapping=core.read(p)if p.exists()else dict(overrides={});mapping['overrides'][n]=core.relative(sample);core.write(p,mapping)
 print(n,'REPAIRED_SAMPLE_DELIVERED',passed,len(checks),flush=True)
if __name__=='__main__':
 for row in rows():
  if label(row)in sys.argv[1:]:run(row)
