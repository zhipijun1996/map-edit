"""Native release consumer and explicitly unqualified partial-route samples."""
import inspect
from pcg.migration import core,physics,godot_package,review040_runtime_v3
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from . import finalize_review040_v1 as previous
from .finalize_review040_v1 import AUTH,folder_for,freeze,qualify
def deliver(row):
 source=inspect.getsource(previous.deliver).replace("backend=review029_runtime_v2 if n=='171'else godot_package","backend=review040_runtime_v3 if n=='206'else godot_package")
 scope={**previous.__dict__,'review040_runtime_v3':review040_runtime_v3};exec(compile(source,__file__,'exec'),scope);scope['deliver'](row)
def partial(row):
 f=folder_for(row);n=row['reviewId'];eng,cs,authors=physics._engine(f,'approved-r040-'+n+'-partial-delivery-v1',physics.FULL_PROTOCOL);items=[];checks=[]
 for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'unqualified-partial-delivery')for c in cs],'candidate-replay')):
  q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e))
  if q['ok']:items.append(physics._recording(c,r))
 core.write(eng.out/'canonical.json',dict(rows=checks,passed=all(r['check']['ok']for r in checks),qualification='UNQUALIFIED',successfulRoutes=[c['route_spec']['id']for c in items]))
 core.write(f/'qualification-not-run.json',dict(status='UNQUALIFIED',formalAttempts=0,independentHoldout='NOT_RUN',reason='bounded control search or unchanged screen did not pass; successful samples do not certify whole Module'))
 core.write(f/'playback-cases.json',dict(cases=items));assert items
 godot_package.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=row['moduleId']);r=godot_package.run_package_validation(f/'playable');core.write(f/'package-result.json',r);print(n,'UNQUALIFIED_NATIVE_SAMPLE',r['passed'],len(items),flush=True)
if __name__=='__main__':
 import sys
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[2:]:globals()[sys.argv[1]](r)
