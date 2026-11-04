if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import inspect,sys
from pcg.migration import core,physics,holdout_guard,pool_protocols,revision060_runtime_v1 as backend
from .continue_revision060_v1 import rows,label,AUTH,FINAL
from .execution_revision060_v1 import frozen_row
from .revision060_content_v1 import decode
from . import finalize_first40_v1 as shared
from . import finalize_revision059_v1 as previous
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
ROOT=FINAL
def folder_for(r):return ROOT/r['moduleId']
def freeze(row,version):
 r=frozen_row(row,version);source=core.REPO/r['outputDirectory'];screen=core.REPO/f'pcg/results/approved-r060-{label(row)}-control-screen-{version}/screen.json';native=source/f'native-preflight-{version}.json';assert core.read(screen)['passed']and core.read(native)['passed']and core.read(screen)['sourceCases']['sha256']==core.sha(source/'cases.json')
 s=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-r060-final-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/revision060_content_v1.py');ns={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(s,__file__,'exec'),ns);ns['freeze'](r)
 f=folder_for(r);doc=core.read(f/'module.mapnote.json');doc['generationContract']['generation']['approvedImplementation']['boundaryInputs']=physics.artifact(f/'physics-input-cases.json');core.write(f/'module.mapnote.json',doc);core.write(f/'static-check.json',core.contract(f/'module.mapnote.json',refresh=True));parameters=core.read(f/'parameters.json');parameters.update(designGeometryChanged=label(r)=='hq02',authorizedDesignAdjustment='middle right edge128→176'if label(r)=='hq02'else None,authorizedNativeCollisionChange='both original P/Q shapes one-way; same native motion'if label(r)=='s12'else None);core.write(f/'parameters.json',parameters);frozen=core.read(f/'frozen.json');frozen.update(module=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'));core.write(f/'frozen.json',frozen);core.write(f/'selection.json',dict(version=version,allGatesPassed=True,screen=physics.artifact(screen),native=physics.artifact(native),executionInputs=physics.artifact(source/'execution-input-freeze.json'),rule='first unchanged clean + bounded screen + native preflight candidate'))
def qualify(r):
 s=inspect.getsource(previous.qualify).replace('approved-r059','approved-r060').replace('approved-revision059','approved-revision060');ns={**previous.__dict__,'folder_for':folder_for,'label':label};exec(compile(s,__file__,'exec'),ns);ns['qualify'](r)
def deliver(r):
 f=folder_for(r);n=label(r);eng,cs,authors=physics._engine(f,'approved-r060-'+n+'-delivery-final-v1',physics.FULL_PROTOCOL);checks=[];items=[]
 for i,(c,raw,e)in enumerate(eng.run([physics.fresh(c,'delivery')for c in cs],'native-delivery')):
  q=checked_purpose(authors[i],c,raw);checks.append(dict(case=c,check=q,evidence=e))
  if q['ok']:items.append(physics._recording(c,raw))
 core.write(eng.out/'canonical.json',dict(passed=len(items)==len(cs),rows=checks));assert len(items)==len(cs),(n,'canonical_delivery_failed');core.write(f/'playback-cases.json',dict(cases=items));backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=r['moduleId']);result=backend.run_package_validation(f/'playable');core.write(f/'package-result.json',result);print(n,'NATIVE_DELIVERY',result['passed'],len(items),flush=True)
if __name__=='__main__':
 for r in rows():
  wanted=sys.argv[3:]if sys.argv[1]=='freeze'else sys.argv[2:]
  if label(r)in wanted:(freeze(r,sys.argv[2])if sys.argv[1]=='freeze'else globals()[sys.argv[1]](r))
