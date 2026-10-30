"""Freeze the first unchanged fully screened/native candidate per specification."""
import inspect
from pcg.migration import core,physics,pool_protocols,holdout_guard,ideas_runtime_v2 as backend
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from . import finalize_first40_v1 as shared
from .new_ideas_v1 import AUTH,rows,label
from .ideas_content_v1 import decode
ROOT=core.REPO/'pcg/manual_review/implementation/new-ideas-final-v1'
def folder_for(row):return ROOT/row['moduleId']
def freeze(row,version):
 f=core.REPO/row['outputDirectory'];screen=core.REPO/'pcg/results'/('approved-ideas-'+label(row)+'-control-screen-'+version+'/screen.json');native=f/('native-preflight-'+version+'.json');assert core.read(screen)['passed']and core.read(native)['passed']and core.read(screen)['sourceCases']['sha256']==core.sha(f/'cases.json')
 core.write(f/'selection.json',dict(version=version,screen=physics.artifact(screen),nativePreflight=physics.artifact(native),rule='first unchanged version passing all gates'))
 source=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-newideas-final-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/ideas_content_v1.py');scope={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(source,__file__,'exec'),scope);scope['freeze'](row)
def qualify(row):
 f=folder_for(row);n=label(row);protocol=physics.FULL_PROTOCOL;guard=holdout_guard.check(f,protocol_path=protocol);cs=core.read(f/'physics-input-cases.json')['cases'];d=core.read(f/'module.mapnote.json');costs=dict(routes=72*len(cs),boundaries=len(physics.seam_cases(cs[0],d))+2*len(cs),counters=sum(len(physics.counter_cases(c))for c in cs));assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
 core.write(f/'preflight.json',dict(guard=guard,protocol=physics.artifact(protocol),costs=costs,maximumAttempts=sum(costs.values()),stopping='one formal version, no holdout tuning',boundaryExtension=physics.artifact(core.REPO/'pcg/migration/ideas_boundary_v1.py')))
 run='approved-ideas-'+n+'-qualified-final-v1';r=physics.run(f,run,protocol_path=protocol);core.write(f/'qualification.json',dict(passed=r['passed'],actualAttempts=r['actualAttempts'],report=physics.artifact(core.REPO/'pcg/results'/run/'migration-physics.json')));print(n,'QUALIFIED',r['passed'],r['actualAttempts'],flush=True)
def deliver(row):
 f=folder_for(row);eng,cs,authors=physics._engine(f,'approved-ideas-'+label(row)+'-delivery-final-v1',physics.FULL_PROTOCOL);checks=[];items=[]
 for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'delivery')for c in cs],'native-delivery')):
  q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e))
  if q['ok']:items.append(physics._recording(c,r))
 core.write(eng.out/'canonical.json',dict(passed=len(items)==len(cs),rows=checks));assert len(items)==len(cs)
 core.write(f/'playback-cases.json',dict(cases=items));backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=row['moduleId']);p=backend.run_package_validation(f/'playable');core.write(f/'package-result.json',p);print(label(row),'NATIVE',p['passed'],flush=True)
if __name__=='__main__':
 import sys
 for r in rows():
  if label(r)in sys.argv[3:]if sys.argv[1]=='freeze'else label(r)in sys.argv[2:]:
   (freeze(r,sys.argv[2])if sys.argv[1]=='freeze'else globals()[sys.argv[1]](r))
