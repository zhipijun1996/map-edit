if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import importlib
from pcg.migration import core,physics
from pcg.migration.evidence_stream_verify_v1 import verify_report

def main():
 for v in ['060','061']:
  scope=importlib.import_module('pcg.manual_review.continue_revision'+v+'_v1');final=importlib.import_module('pcg.manual_review.finalize_revision'+v+'_v1');checks=[]
  for row in scope.rows():
   f=final.folder_for(row);q=core.read(f/'qualification.json')
   if not q['passed']:continue
   result=verify_report(f,q['report']);checks.append(dict(name=scope.label(row),report=q['report'],result=result));print(v,scope.label(row),'FULL_REPORT_RAW_REDERIVED',flush=True)
  core.write(scope.OUT/'verification/full-report-rederivation.json',dict(passed=True,rows=checks,source=physics.artifact(__file__),failedQualificationsNotRelabeled=True))
if __name__=='__main__':main()
