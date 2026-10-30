"""Checkpoint each complete read-only raw rederivation; never rerun physics."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import importlib,sys
from pcg.migration import core,physics
from pcg.migration.evidence_stream_verify_v1 import verify_report

def main():
 for v in ['060','061']:
  scope=importlib.import_module('pcg.manual_review.continue_revision'+v+'_v1');final=importlib.import_module('pcg.manual_review.finalize_revision'+v+'_v1');checks=[]
  for row in scope.rows():
   f=final.folder_for(row);q=core.read(f/'qualification.json');n=scope.label(row)
   if not q['passed']:continue
   checkpoint=scope.OUT/('verification/rederived-'+n+'.json')
   if not checkpoint.exists():
    report=verify_report(f,q['report']);core.write(checkpoint,dict(name=n,report=q['report'],passed=True,actualAttempts=report['actualAttempts'],verifier=physics.artifact('pcg/migration/evidence_stream_verify_v1.py'),physicsRerun=False));print(v,n,'FULL_REPORT_RAW_REDERIVED',flush=True)
   else:assert core.read(checkpoint)['report']==q['report']
   checks.append(physics.artifact(checkpoint))
  core.write(scope.OUT/'verification/full-report-rederivation.json',dict(passed=True,rows=checks,source=physics.artifact(__file__),failedQualificationsNotRelabeled=True))
if __name__=='__main__':main()
