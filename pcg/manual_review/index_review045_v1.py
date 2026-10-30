"""Final approved scope, partial route results and honest native/video limits."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import json,shutil
from collections import Counter
from pathlib import Path
from pcg.migration import core,physics
from .refresh_review045_v1 import OUT,AUTH,rows
from .finalize_review045_v1 import folder_for
from .audit_review045_v1 import QUALIFIED
BLOCKERS={
 '42':dict(reason='Only 4/6 formal routes pass. entry-to-exit moderate calibration 6/12 and C-to-exit 5/12 are below the unchanged 0.65 gate. Their holdouts were correctly skipped. Observed hook/jump/upper landing timing can miss the original OR chest approach or right dock.',nextAction='In a separately registered continuation, replace jump/shot timing with actual hook completion, actual upper landing and original chest interaction predicates. Do not tune this frozen formal version on observed conditions.',designDefectProven=False),
 '50':dict(reason='All six clean and native routes pass. Final unchanged moderate screen: C-to-entry 4/6 and C-to-exit 3/6; other four 6/6. Lower hook contacts, but second upper hook can miss under aim/timing noise and the actor falls outside the rectangle.',nextAction='Use a live safe casting position and completed first-hook state before casting the upper ring, with unchanged actual range and single air shot. If geometry changes are desired, review moving the upper anchor farther from the pillar or restoring a landing; neither is applied.',designDefectProven=False),
 '51':dict(reason='Neither final clean direction is damage-free. Outbound first hook projectile contacts, but the body rises into danger_0 and resets at frame34 (HP4); reverse reaches the central safe floor then clips the hazard during leftward takeoff. Native package repeats actual damage and is rejected.',nextAction='New bounded continuation could separate jump release from hook cancellation using observed motion, and launch from farther inside the central safe floor. Any restored intermediate landing or wider clearance is a design change requiring separate approval; not applied.',designDefectProven=False),
 '52':dict(reason='Neither final clean direction is damage-free. Same first-hook ceiling-hazard contact at frame34; reverse reaches central floor but clips the left bottom hazard on takeoff. Compiled manual candidate exists; real native replay fails with HP4.',nextAction='Resolve jump-release/hook scheduling and safe central takeoff under real collision geometry. Keep one actual air shot; original anchor contact does not refill shots. Optional landing/anchor/clearance changes require separate design approval.',designDefectProven=False),
 '220':dict(reason='Four of six final clean and native directions pass; C-to-A/B-to-A time out. Actual airborne hits and shot refunds now work (three diver hits; B route also one ground-enemy hit). The final rise/leftward crossing meets the underside or reaches the A ledge after losing height; no reliable upper landing.',nextAction='Next bounded round should align the final recoil outside the solid A platform and reach above its top before moving left. Reuse accepted hit/refund observation; do not grant shots or move enemies. This is a control hypothesis, not proof of impossibility.',designDefectProven=False)}
def main():
 results=[];nativecases=0;nativepass=0;movies_total=0;strict_total=0
 for row in sorted(rows(),key=lambda r:int(r['reviewId'])):
  n=row['reviewId'];f=folder_for(row);doc=core.read(f/'module.mapnote.json');passed=n in QUALIFIED
  result=dict(schema='pcg/approved-design-implementation-result/v10',reviewId=n,moduleId=row['moduleId'],design=physics.artifact(core.REPO/row['designFile']),designVersion=row['designVersion'],authorization=physics.artifact(AUTH/'request.json'),status='PASS'if passed else'UNQUALIFIED',implementationVersion=doc['generationContract']['contentVersion'],module=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),physicsCases=physics.artifact(f/'physics-input-cases.json'),humanPlaytest='UNKNOWN',productionApproval=False,scope=dict(orientation='identity',mirror='UNKNOWN',closureConfigurations='UNKNOWN',fullMap='UNKNOWN'))
  qpath=f/('qualification-repaired.json'if n=='62'else'qualification.json')
  if qpath.exists():
   q=core.read(qpath);r=core.read(core.resolve_artifact(q['report']['path']));assert r['passed']==passed;stats=[]
   for route in r['routes']:
    v=dict(routeId=route['routeId'],passed=route['passed'])
    for stage in ['calibration','holdout']:
     if isinstance(route[stage],dict):
      s=core.read(core.resolve_artifact(route[stage]['path']))['stats'];v[stage]={k:dict(passed=s[k]['purpose_valid'],trials=s[k]['trials'])for k in ['clean','mild','moderate']}
     else:v[stage]='NOT_RUN'
    stats.append(v)
   result.update(qualificationReport=q['report'],formalAttempts=r['actualAttempts'],routes=stats)
   if n=='62':result.update(originalFailure=physics.artifact(core.REPO/'pcg/results/approved-r045-62-qualified-final-v1/migration-physics.json'),newBoundaryTrials=2,newIndependentHoldout=False,unchangedNominalAndHoldout=True)
  else:result.update(formalAttempts=0,holdout='NOT_RUN')
  if not passed:result.update(blocker=BLOCKERS[n],stoppingRecord=physics.artifact(OUT/'verification/revision-budget.json'),budgetExhausted=n!='42',formalSelectedVersionExhausted=n=='42')
  draft=core.REPO/row['outputDirectory']
  if(draft/'selection.json').exists():result['selectedControl']=core.read(draft/'selection.json')
  else:
   result['lastControlVersion']={'50':'v9','51':'v7','52':'v7','220':'v8'}[n]
   if n=='50':
    screen=core.REPO/'pcg/results/approved-r045-50-control-screen-v9/screen.json';result.update(screen=physics.artifact(screen),screenCounts=core.read(screen)['counts'])
  root=core.REPO/'pcg/results'/('approved-r045-'+n+('-delivery-final-v1'if n in QUALIFIED|{'42'}else'-partial-delivery-v1'));c=core.read(root/'canonical.json');result['canonicalDelivery']=dict(artifact=physics.artifact(root/'canonical.json'),successfulRoutes=[v['case']['route_spec']['id']for v in c['rows']if v['check']['ok']],failedRoutes=[dict(route=v['case']['route_spec']['id'],reasons=v['check']['reasons'])for v in c['rows']if not v['check']['ok']])
  pfile=f/'package-result.json';p=core.read(pfile);nativecases+=p['canonical_cases'];nativepass+=bool(p['passed']);result['nativePlayable']=dict(path=core.relative(f/'playable'),manifest=physics.artifact(f/'playable/godot-package.json'),result=physics.artifact(pfile),passed=p['passed'],compiled=p['compiled'],replayCases=p['canonical_cases'],wholeModuleQualification=result['status'],manualCandidateOnly=n in {'51','52'})
  videos=[]
  for path in sorted((OUT/'videos').glob(n+'-*/manifest.json')):
   m=core.read(path);diff=core.read(path.parent/'strict-comparison-failed.json')if m.get('reviewOnly')else None;log=next(path.parent.glob('*.record.log')).read_text();actual=json.loads(next(v for v in log.splitlines()if v.startswith('WORKSHOP_MOVIE_RESULT ')).split(' ',1)[1]);assert (actual['safe']and actual['hp']==5)or n in {'51','52'}
   videos.append(dict(routeId=m['scope']['route']['id'],manifest=physics.artifact(path),movie=physics.artifact(path.parent/m['clips'][0]['file']),durationSeconds=m['clips'][0]['duration'],comparison='FAIL; review-only'if diff else'PASS',differenceFields=dict(Counter(v['field']for v in diff['differences']))if diff else{},nativeOutcome=actual,failedRouteFootage=n in {'51','52'}));movies_total+=1;strict_total+=not bool(diff)
  assert videos,(n,'missing movie');result['videos']=videos;core.write(OUT/(n+'.json'),result);results.append(dict(reviewId=n,status=result['status'],result=physics.artifact(OUT/(n+'.json')),formalAttempts=result['formalAttempts']))
 prior=core.REPO/'feedback/manual-review/implementation-results/review-031-v1';old=core.read(prior/'196.json');core.write(OUT/'196.json',dict(**old,carriedForward=True,previousResult=physics.artifact(prior/'196.json'),unchangedCurrentVersion=True));results.append(dict(reviewId='196',status='DESIGN_CONFLICT',carriedForward=True,result=physics.artifact(OUT/'196.json'),formalAttempts=0))
 req=core.read(AUTH/'request.json');index=dict(schema='pcg/approved-implementation-refresh-index/v5',baseMain=req['baseMain'],latestMainRefresh=physics.artifact(OUT/'verification/latest-main.json'),latestHandoffApproved=83,subsequentlyApprovedNotInFrozenRound=['idea-orbit-choice-001'],scopeIds=req['keepIds'],retryIds=req['retryIds'],carriedForwardUnresolved=['196'],newlyQualified=sorted(QUALIFIED,key=int),notFullyQualified=['42','50','51','52','196','220'],totalApproved=82,totalCurrentQualified=67+len(QUALIFIED),retained157TopPlusOneBlock=True,retained171174175Clarifications=True,duplicate61=physics.artifact(OUT/'verification/duplicate61.json'),deletedThisRefresh=8,totalDeleted=143,currentActiveTemplates=len(core.read(core.ACTIVE/'catalog.json')['modules']),pendingUnapproved=req['pendingIds'],formalAttempts=sum(r['formalAttempts']for r in results),nativePackages=14,nativeReplayPassedPackages=nativepass,nativeCases=nativecases,currentVideos=movies_total,currentStrictVideoPass=strict_total,historicalFailuresRetained=True,sourceAudit=physics.artifact(OUT/'verification/source-audit.json'),deepProofs=physics.artifact(OUT/'verification/deep-proofs.json'),archive=physics.artifact(core.REPO/'pcg/archives/approved-review045-implementation-v1/manifest.json'),results=results,productionApproval=False)
 assert index['totalCurrentQualified']==76 and index['currentActiveTemplates']==82
 core.write(OUT/'index.json',index)
 for path in Path('/tmp').glob('review045-*.log'):
  if path.is_file()and not path.name.startswith(('review045-publish','review045-public')):shutil.copy2(path,OUT/'verification'/path.name)
 print('CURRENT_76_OF_82',index['formalAttempts'],nativecases,movies_total,strict_total,flush=True)
if __name__=='__main__':main()
