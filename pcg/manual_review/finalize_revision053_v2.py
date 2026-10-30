"""Deliver native samples independently of their complete qualification status."""
import inspect,sys
from pcg.migration import core,physics,godot_package,revision053_runtime_v1
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from . import finalize_revision053_v1 as previous,finalize_first40_v1 as shared
from .continue_revision053_v1 import rows,label,AUTH
from .prepare_revision053_v1 import decode
ROOT=previous.ROOT
folder_for=previous.folder_for

def freeze(row,version,demo=False):
 draft=core.REPO/row['outputDirectory'];screen=core.REPO/f'pcg/results/approved-r053-{label(row)}-control-screen-{version}/screen.json';native=draft/f'native-preflight-{version}.json'
 assert core.read(native)['passed']and core.read(screen)['sourceCases']['sha256']==core.sha(draft/'cases.json')
 good=core.read(screen)['passed'];assert good or demo
 source=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-r053-final-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/prepare_revision053_v1.py')
 namespace={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(source,__file__,'exec'),namespace);namespace['freeze'](row)
 f=folder_for(row)
 if label(row)in ['three','lift']:
  d=core.read(f/'module.mapnote.json');d['generationContract']['generation']['approvedImplementation']['boundaryInputs']=physics.artifact(f/'physics-input-cases.json');core.write(f/'module.mapnote.json',d);core.write(f/'static-check.json',core.contract(f/'module.mapnote.json',refresh=True));frozen=core.read(f/'frozen.json');frozen['module']=physics.artifact(f/'module.mapnote.json');core.write(f/'frozen.json',frozen)
 core.write(f/'selection.json',dict(version=version,allScreenPassed=good,selectedForFormal=good,screen=physics.artifact(screen),native=physics.artifact(native),rule='first unchanged all gates passing candidate; explicit demonstration freeze on bounded-stop only'))
 if not good:core.write(f/'qualification-not-run.json',dict(passed=False,status='UNQUALIFIED',independentHoldoutUsed=False,reason='bounded prospective control search stopped without all-route screen pass; native clean demonstration only',designImpossible=False))
def qualify(row):return previous.qualify(row)
def deliver(row):
 f=folder_for(row);n=label(row);eng,cs,authors=physics._engine(f,'approved-r053-'+n+'-delivery-final-v1',physics.FULL_PROTOCOL);checks=[];items=[]
 for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'delivery')for c in cs],'native-delivery')):
  q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e))
  if q['ok']:items.append(physics._recording(c,r))
 core.write(eng.out/'canonical.json',dict(passed=len(items)==len(cs),rows=checks));assert len(items)==len(cs),(n,'canonical_delivery_failed')
 core.write(f/'playback-cases.json',dict(cases=items));backend=revision053_runtime_v1 if n in ['196','three','lift']else godot_package
 backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=row['moduleId']);result=backend.run_package_validation(f/'playable');core.write(f/'package-result.json',result);print(n,'DELIVERY_NATIVE',result['passed'],len(items),flush=True)
if __name__=='__main__':
 for row in rows():
  wanted=sys.argv[3:]if sys.argv[1]in ['freeze','demo']else sys.argv[2:]
  if label(row)in wanted:(freeze(row,sys.argv[2],sys.argv[1]=='demo')if sys.argv[1]in ['freeze','demo']else globals()[sys.argv[1]](row))
