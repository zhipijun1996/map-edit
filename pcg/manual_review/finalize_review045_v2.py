"""Explicitly unqualified samples; failed replays remain failed."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,physics,godot_package
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .refresh_review045_v1 import rows
from .finalize_review045_v1 import folder_for,freeze

def partial(row):
 f=folder_for(row);n=row['reviewId'];freeze(row)
 eng,cs,authors=physics._engine(f,'approved-r045-'+n+'-partial-delivery-v1',physics.FULL_PROTOCOL);checks=[];good=[];bad=[]
 for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'unqualified-partial-delivery')for c in cs],'candidate-replay')):
  q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e));(good if q['ok']else bad).append(physics._recording(c,r))
 core.write(eng.out/'canonical.json',dict(rows=checks,passed=len(good)==len(cs),qualification='UNQUALIFIED',successfulRoutes=[c['route_spec']['id']for c in good]))
 core.write(f/'qualification-not-run.json',dict(status='UNQUALIFIED',formalAttempts=0,independentHoldout='NOT_RUN',reason='bounded development exhausted without all clean/screen/native gates; no geometric impossibility claim'))
 # If no successful direction exists, provide a loadable manual candidate and
 # retain its failed native replay receipts, never a successful route label.
 core.write(f/'playback-cases.json',dict(cases=good or bad));godot_package.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=row['moduleId']);p=godot_package.run_package_validation(f/'playable');core.write(f/'package-result.json',p)
 core.write(f/'delivery-scope.json',dict(status='UNQUALIFIED',successfulDirections=len(good),requestedDirections=len(cs),failedReplayOnly=not good,nativeReplayPassed=p['passed'],manualPlaytest='UNKNOWN'))
 print(n,'PARTIAL_NATIVE',p['passed'],len(good),len(cs),flush=True)
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:partial(r)
