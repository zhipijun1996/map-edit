"""Repair only the five observed calibration failures, never holdout inputs."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,sys
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .run_revision065_lift_v1 import frozen_row,rows
from .continue_revision065_lift_v1 import OUT
def main():
 version=sys.argv[1];row=frozen_row(rows()[0],version);f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];old=core.REPO/'pcg/results/approved-r065-lift-qualified-final-v1';cal=core.read(old/'calibration-0.json');failed=[r for r in cal['rows']if not r['purpose']['ok']];assert len(failed)==5
 inputs=[];origins=[]
 for entry in failed:
  e=entry['evidence'];p=old/'physics'/(e['batch']+'.input.json');c=copy.deepcopy(core.read(p)['cases'][e['index']]);c['id']+='-control-repair-'+version;c['control_plan']=copy.deepcopy(cs[0]['control_plan']);c['generation_rule']=copy.deepcopy(cs[0]['generation_rule']);c['module_sha256']=physics.module_hash(c);inputs.append(c);origins.append(dict(source=physics.artifact(p),index=e['index'],priorFailure=entry['purpose']['reasons']))
 eng,_,authors=physics._engine(f,'approved-r065-lift-known-calibration-repair-'+version,physics.FULL_PROTOCOL);checks=[]
 for c,r,e in eng.run(inputs,'known-calibration-control-repair'):
  q=checked_purpose(authors[0],c,r);checks.append(dict(caseId=c['id'],passed=q['ok'],check=q,evidence=e));print(c['id'],q['ok'],q['reasons'],flush=True)
 core.write(eng.out/'repair-check.json',dict(passed=all(q['passed']for q in checks),rows=checks,originals=origins,scope='Same five observed calibration phases, enemy cooldowns and noise; only genuine control program changes. No holdout diagnostic or new seed.',source=physics.artifact(__file__)));print('R065_KNOWN_CALIBRATION_REPAIR',all(q['passed']for q in checks),flush=True)
if __name__=='__main__':main()
