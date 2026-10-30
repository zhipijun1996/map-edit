"""Dependent completion only; wait for the already-running frozen S12 campaign."""
import subprocess,time
from pcg.migration import core,physics
from .continue_revision062_v1 import OUT,rows,label
from .finalize_revision062_v1 import folder_for

def run(module,*args):subprocess.run(['python3','-m',module,*args],check=True)
def main():
 f=folder_for(next(r for r in rows()if label(r)=='rs12'))
 while not(f/'qualification.json').exists():time.sleep(5)
 run('pcg.manual_review.apply_partial_holdout_guard_v1');run('pcg.manual_review.check_partial_holdout_exposure_v1')
 from pcg.migration import holdout_guard
 import importlib;importlib.reload(holdout_guard)
 state=holdout_guard.refresh();core.write(OUT/'verification/partial-holdout-lock-snapshot.json',state);core.write(OUT/'verification/partial-exposure-locks.json',dict(passed=True,counts=state['counts'],partialExposures=len(state.get('partialExposures',{})),locks=physics.artifact(OUT/'verification/partial-holdout-lock-snapshot.json'),activeLockPath=core.relative(holdout_guard.LOCKS),freshnessRulesNotRelaxed=True))
 if core.read(f/'qualification.json')['passed']:run('pcg.manual_review.verify_revision062_reports_v1','rs12')
 verified=[]
 for r in rows():
  if core.read(folder_for(r)/'qualification.json')['passed']:
   p=OUT/('verification/rederived-'+label(r)+'.json');assert core.read(p)['passed'];verified.append(physics.artifact(p))
 core.write(OUT/'verification/full-report-rederivation.json',dict(passed=True,rows=verified,knownPoolReplayNotIndependent=physics.artifact(OUT/'verification/rederived-hq07.json'),knownPoolBlocked=physics.artifact(OUT/'verification/hq07-fresh-pool-blocked.json'),source=physics.artifact(__file__),failedOrKnownQualificationsNotRelabeled=True))
 run('pcg.manual_review.audit_revision062_v1');run('pcg.manual_review.bundle_revision062_v1');run('pcg.manual_review.report_revision062_v1');run('pcg.manual_review.archive_revision062_v1');print('062_EVIDENCE_READY',flush=True)
if __name__=='__main__':main()
