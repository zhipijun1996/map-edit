"""Ship the calibration-derived HQ07 repair without erasing its failed formal run."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,gzip,json
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .continue_revision063_v1 import rows,label,OUT
from . import finalize_revision063_v1 as final
def main():
 row=next(r for r in rows()if label(r)=='hq07');original=final.folder_for(row);failed=core.read(original/'qualification.json');assert failed['passed']is False
 final.ROOT=core.REPO/'pcg/manual_review/implementation/revision-063-repaired-samples-v1'
 final.freeze(row,'hq07-v8',demo=True);sample=final.folder_for(row)
 report=core.resolve_artifact(failed['report']['path']);cal=core.read(report.parent/'calibration-1.json');template=next(c for c in core.read(sample/'physics-input-cases.json')['cases'] if c['route_spec']['from_port']=='R');inputs=[];lineage=[]
 for before in cal['rows']:
  if before['purpose']['ok']:continue
  e=before['evidence'];input_path=report.parent/'physics'/(e['batch']+'.input.json');old=core.read(input_path)['cases'][e['index']];new=copy.deepcopy(old);new['control_plan']=copy.deepcopy(template['control_plan']);new['id']+='-r063-repair-replay';inputs.append(new)
  lineage.append(dict(originalInput=physics.artifact(input_path),originalIndex=e['index'],originalFailure=before['purpose'],changedFields=['id','control_plan'],samePhysicalConditionsAndNoise=True))
 assert len(inputs)==4
 engine,cs,authors=physics._engine(sample,'approved-r063-hq07-known-calibration-repair-v8',physics.FULL_PROTOCOL);checks=[]
 for c,raw,e in engine.run(inputs,'same-calibration-input-repair'):
  q=checked_purpose(physics.author_for(c),c,raw);checks.append(dict(check=q,evidence=e));assert q['ok'],q
 core.write(engine.out/'repair-check.json',dict(passed=True,rows=checks,lineage=lineage,newIndependentHoldout=False,originalFormalFailureRetained=failed['report'],diagnosticBudget=dict(clean=1,screen=13,knownFailuresReplayed=4,totalPerRepairedRoute=18)))
 q=core.read(sample/'qualification.json');q.update(status='REPAIRED_SAMPLE_FORMAL_PENDING',priorFailedQualification=failed,knownCalibrationFailuresRepaired=physics.artifact(engine.out/'repair-check.json'),reason='New station824 fixes four observed calibration escapes and passes clean/screen/native. The one selected formal campaign failed; no second formal candidate or pool was allocated.');core.write(sample/'qualification.json',q)
 final.deliver(row)
 core.write(OUT/'delivery-selection.json',dict(overrides={'hq07':core.relative(sample)},reason='Use the repaired native sample while keeping the failed formal candidate immutable.'))
 print('HQ07_REPAIRED_SAMPLE',len(checks),'KNOWN_CALIBRATION_FAILURES_PASS',flush=True)
if __name__=='__main__':main()
