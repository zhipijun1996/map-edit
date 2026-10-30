import inspect,sys
from pcg.migration import core,physics,holdout_guard,pool_protocols
from .continue_revision063_v1 import rows,label,AUTH,OUT,FINAL
from .execution_revision063_v1 import frozen_row
from .revision063_content_v1 import decode
from .native_preflight_revision063_v1 import backend
from . import finalize_first40_v1 as shared,finalize_revision059_v1 as previous
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
ROOT=FINAL
def folder_for(r):return ROOT/r['moduleId']
def freeze(row,version,demo=False):
 r=frozen_row(row,version);source=core.REPO/r['outputDirectory'];screen=core.REPO/f'pcg/results/approved-r063-{label(row)}-control-screen-{version}/screen.json';native=source/f'native-preflight-{version}.json'
 assert core.read(native)['passed'] and (demo or core.read(screen)['passed']) and core.read(screen)['sourceCases']['sha256']==core.sha(source/'cases.json')
 s=inspect.getsource(shared.freeze).replace('approved-first40-final-v1-','approved-r063-final-v1-').replace('pcg/manual_review/first30_content_v2.py','pcg/manual_review/revision063_content_v1.py');ns={**shared.__dict__,'AUTH':AUTH,'ROOT':ROOT,'folder_for':folder_for,'decode':decode};exec(compile(s,__file__,'exec'),ns);ns['freeze'](r)
 f=folder_for(r);doc=core.read(f/'module.mapnote.json');doc['generationContract']['generation']['approvedImplementation']['boundaryInputs']=physics.artifact(f/'physics-input-cases.json');core.write(f/'module.mapnote.json',doc);core.write(f/'static-check.json',core.contract(f/'module.mapnote.json',refresh=True));frozen=core.read(f/'frozen.json');frozen['module']=physics.artifact(f/'module.mapnote.json');core.write(f/'frozen.json',frozen)
 core.write(f/'selection.json',dict(version=version,allGatesPassed=core.read(screen)['passed'],selectedForFormal=not demo,screen=physics.artifact(screen),native=physics.artifact(native),rule='First unchanged clean + screen + native passing candidate; demo is explicitly unqualified.'))
 if demo:core.write(f/'qualification.json',dict(passed=False,status='UNQUALIFIED',reason='Control search stopped without all screen gates; real native sample only',independentHoldoutUsed=False))
def upgrade_declaration():
 from .prepare_revision063_v1 import old_folder
 values=[]
 for r in rows():
  if not label(r).startswith(('lt-','lb-')):continue
  f=folder_for(r);old=old_folder(r);q=core.read(old/'qualification-supplemented.json');assert q['passed'] and q['fullV2Qualification']is False
  values.append(dict(reviewId=r['reviewId'],designVersion=r['designVersion'],source=holdout_guard._identity(f),documentSha256=core.sha(f/'module.mapnote.json'),canonicalCasesSha256=core.sha(f/'physics-input-cases.json'),legacyCases=physics.artifact(old/'physics-input-cases.json'),passingSupplement=q['report']))
 p=AUTH/'six-legacy-full-v2-upgrade.json';assert not p.exists();core.write(p,dict(schema='pcg/legacy-passing-program-full-v2-upgrade/v1',taskAuthorization=physics.artifact(AUTH/'request.json'),maximumPoolsPerSource=1,seedsAllocated=False,rows=values,selection='All six unchanged legacy programs are included; no choosing from new full v2 results. Preserve every old pass/failure and supplement; never reroll.'))
 print('SIX_PROSPECTIVE_UPGRADE_FROZEN',flush=True)
def qualify(r):
 f=folder_for(r);n=label(r);protocol=pool_protocols.runtime_protocol(f,new_run=True) if core.read(f/'migration.json').get('holdoutPool') else physics.FULL_PROTOCOL;registration=None
 try:guard=holdout_guard.check(f,protocol_path=protocol)
 except holdout_guard.HoldoutConflict:
  reference=physics.artifact(AUTH/'six-legacy-full-v2-upgrade.json') if n.startswith(('lt-','lb-')) else None
  registration=holdout_guard.register_pool(f,'approved-revision063-v1-'+n,protocol_upgrade=reference);protocol=pool_protocols.runtime_protocol(f,new_run=True);guard=holdout_guard.check(f,protocol_path=protocol)
 assert core.read(protocol)['schema']=='pcg/module-migration-protocol/v2'
 cs=core.read(f/'physics-input-cases.json')['cases'];doc=core.read(f/'module.mapnote.json');costs=dict(routes=sum(72 if c.get('enemies')or c.get('saws')or c.get('moving_platforms')else 50 for c in cs),boundaries=len(physics.seam_cases(cs[0],doc))+2*len(cs),counters=sum(len(physics.counter_cases(c))for c in cs));assert sum(costs.values())<=core.read(protocol)['maximumAttemptsPerModule']
 core.write(f/'preflight.json',dict(protocol=physics.artifact(protocol),guard=guard,registration=registration,costs=costs,stopping='One first FULL v2 candidate, one allocated pool. No reroll or holdout tuning.'))
 run='approved-r063-'+n+'-qualified-final-v1';report=physics.run(f,run,protocol_path=protocol);core.write(f/'qualification.json',dict(passed=report['passed'],actualAttempts=report['actualAttempts'],report=physics.artifact(core.REPO/'pcg/results'/run/'migration-physics.json')));print(n,'QUALIFIED_FULL_V2',report['passed'],report['actualAttempts'],flush=True)
def deliver(r):
 f=folder_for(r);n=label(r);eng,cs,authors=physics._engine(f,'approved-r063-'+n+'-delivery-final-v1',physics.FULL_PROTOCOL);checks=[];items=[]
 for i,(c,raw,e)in enumerate(eng.run([physics.fresh(c,'delivery')for c in cs],'native-delivery')):
  q=checked_purpose(authors[i],c,raw);checks.append(dict(case=c,check=q,evidence=e))
  if q['ok']:items.append(physics._recording(c,raw))
 core.write(eng.out/'canonical.json',dict(passed=len(items)==len(cs),rows=checks));assert len(items)==len(cs),(n,'canonical_delivery_failed');core.write(f/'playback-cases.json',dict(cases=items));b=backend(n);b.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=r['moduleId']);result=b.run_package_validation(f/'playable');core.write(f/'package-result.json',result);print(n,'NATIVE_DELIVERY',result['passed'],len(items),flush=True)
if __name__=='__main__':
 if sys.argv[1]=='upgrade-declaration':upgrade_declaration()
 else:
  for r in rows():
   wanted=sys.argv[3:]if sys.argv[1]in ['freeze','demo']else sys.argv[2:]
   if label(r)in wanted:
    if sys.argv[1]in ['freeze','demo']:freeze(r,sys.argv[2],sys.argv[1]=='demo')
    else:globals()[sys.argv[1]](r)
