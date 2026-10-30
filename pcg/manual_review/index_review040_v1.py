"""Current scope, original failures and exact limits; no production admission."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import json,shutil
from collections import Counter
from pathlib import Path
from pcg.migration import core,physics
from .prepare_review040_v3 import OUT,AUTH,rows
from .finalize_review040_v1 import folder_for
from .audit_review040_v1 import QUALIFIED
BLOCKERS={
 '115':dict(reason='Forward route control is unreliable; reverse is clean/mild/moderate 1/6/6. Random ferry phase can put the carried enemy on the left lip. The final bank-fire program also fires again before returning to x240, recoils outside the rectangle and times out.',nextAction='Add a live staging-position and inactive-burst predicate before every bank shot; clear the actual left-lip enemy before recoil boarding. Retest both directions in a separately registered bounded round.',designDefectProven=False),
 '220':dict(reason='Five of six clean routes pass. C-to-A first consumes its only charge with a ground recoil, so its next airborne shot is rejected before an enemy-hit refund can occur.',nextAction='Reuse the working B-to-A ascent from the 500,562 step, with live enemy phase and direction observation, and omit the initial ground shot. This is an untested next hypothesis.',designDefectProven=False),
 '223':dict(reason='All 12 clean directions pass. Final C-to-D moderate screen is 4/6, below the frozen 5/6 gate; actual harm and apex timeout remain. Full native replay separately loses HP on C-to-A (317 frames, HP4); the original failed package is retained.',nextAction='Make the C-entry combat and transition depend on real accepted hits and landing state, then resolve the native timing divergence. Keep geometry and the original thresholds.',designDefectProven=False),
 '225':dict(reason='Four of six clean directions pass; B-to-A/C remain unqualified. The 320px rise exceeds ordinary jump plus one recoil (~304px). No reliable real airborne-hit refund sequence was found. The final short bait jump lands before the 0.6s telegraph completes, so the diver does not reach the awaited dive height.',nextAction='Test a full bait jump that maintains native engagement through telegraph, then use a real airborne hit and refund for the second recoil. Do not lower the platform, move the enemy or grant shots without design authorization.',designDefectProven=False)}
def main():
 results=[];native=0;movies_total=0;strict_total=0
 for row in sorted(rows(),key=lambda r:int(r['reviewId'])):
  n=row['reviewId'];f=folder_for(row);doc=core.read(f/'module.mapnote.json');passed=n in QUALIFIED
  result=dict(schema='pcg/approved-design-implementation-result/v9',reviewId=n,moduleId=row['moduleId'],design=physics.artifact(core.REPO/row['designFile']),designVersion=row['designVersion'],authorization=physics.artifact(AUTH/'request.json'),status='PASS'if passed else'UNQUALIFIED',implementationVersion=doc['generationContract']['contentVersion'],module=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),physicsCases=physics.artifact(f/'physics-input-cases.json'),humanPlaytest='UNKNOWN',productionApproval=False,scope=dict(orientation='identity',mirror='UNKNOWN',closureConfigurations='UNKNOWN',fullMap='UNKNOWN'))
  if passed:
   q=core.read(f/('qualification-reanalyzed.json'if n in {'166','206'}else'qualification.json'));r=core.read(core.resolve_artifact(q['report']['path']));assert r['passed'];stats=[]
   for route in r['routes']:
    v=dict(routeId=route['routeId'],passed=route['passed'])
    for stage in ['calibration','holdout']:
     s=core.read(core.resolve_artifact(route[stage]['path']))['stats'];v[stage]={k:dict(passed=s[k]['purpose_valid'],trials=s[k]['trials'])for k in ['clean','mild','moderate']}
    stats.append(v)
   result.update(qualificationReport=q['report'],formalAttempts=r['actualAttempts'],routes=stats)
   if n in {'166','206'}:result.update(originalFailure=q.get('sourceReport',q.get('originalFailure')),newPhysicsAttemptsForReanalysis=0,newIndependentHoldoutForReanalysis=False)
  else:
   result.update(formalAttempts=0,holdout='NOT_RUN',blocker=BLOCKERS[n],budgetExhausted=True,stoppingRecord=physics.artifact(OUT/'verification/revision-budget.json'))
   if n in {'115','223'}:
    screen=core.REPO/'pcg/results'/('approved-r040-'+n+'-control-screen-'+('v10'if n=='115'else'v9'))/'screen.json';result.update(screen=physics.artifact(screen),screenCounts=core.read(screen)['counts'])
  root=core.REPO/'pcg/results'/('approved-r040-'+n+('-delivery-final-v1'if passed else'-partial-delivery-v2'));c=core.read(root/'canonical.json');result['canonicalDelivery']=dict(artifact=physics.artifact(root/'canonical.json'),successfulRoutes=[v['case']['route_spec']['id']for v in c['rows']if v['check']['ok']],failedRoutes=[dict(route=v['case']['route_spec']['id'],reasons=v['check']['reasons'])for v in c['rows']if not v['check']['ok']])
  package=f/('playable-representative-v1'if n=='223'else'playable');pfile=f/('representative-package-result-v1.json'if n=='223'else'package-result.json');p=core.read(pfile);assert p['passed'];native+=p['canonical_cases'];result['nativePlayable']=dict(path=core.relative(package),manifest=physics.artifact(package/'godot-package.json'),result=physics.artifact(pfile),passed=True,replayCases=p['canonical_cases'],wholeModuleQualification=result['status'])
  if n=='223':result['failedFullNativePackage']=physics.artifact(f/'native-full-replay-failure-v1.json')
  videos=[]
  for path in sorted((OUT/'videos').glob(n+'-*/manifest.json')):
   m=core.read(path);diff=core.read(path.parent/'strict-comparison-failed.json')if m.get('reviewOnly')else None;log=next(path.parent.glob('*.record.log')).read_text();actual=json.loads(next(v for v in log.splitlines()if v.startswith('WORKSHOP_MOVIE_RESULT ')).split(' ',1)[1]);assert actual['safe']and actual['hp']==5
   videos.append(dict(routeId=m['scope']['route']['id'],manifest=physics.artifact(path),movie=physics.artifact(path.parent/m['clips'][0]['file']),durationSeconds=m['clips'][0]['duration'],comparison='FAIL; review-only'if diff else'PASS',differenceFields=dict(Counter(v['field']for v in diff['differences']))if diff else{},nativeOutcome=actual));movies_total+=1;strict_total+=not bool(diff)
  assert videos;result['videos']=videos;core.write(OUT/(n+'.json'),result);results.append(dict(reviewId=n,status=result['status'],result=physics.artifact(OUT/(n+'.json')),formalAttempts=result['formalAttempts']))
 prior=core.REPO/'feedback/manual-review/implementation-results/review-031-v1';old=core.read(prior/'196.json');core.write(OUT/'196.json',dict(**old,carriedForward=True,previousResult=physics.artifact(prior/'196.json'),unchangedCurrentVersion=True));results.append(dict(reviewId='196',status='DESIGN_CONFLICT',carriedForward=True,result=physics.artifact(OUT/'196.json'),formalAttempts=0))
 req=core.read(AUTH/'request.json');index=dict(schema='pcg/approved-implementation-refresh-index/v4',baseMain=req['baseMain'],scopeIds=req['keepIds'],carriedForwardUnresolved=['196'],newlyQualified=sorted(QUALIFIED,key=int),notFullyQualified=['115','196','220','223','225'],totalApproved=72,totalCurrentQualified=67,retained157TopPlusOneBlock=True,retained171174175Clarifications=True,deletedThisRefresh=75,totalDeleted=135,currentActiveTemplates=len(core.read(core.ACTIVE/'catalog.json')['modules']),pendingUnapproved=req['pendingIds'],formalAttempts=sum(r['formalAttempts']for r in results),nativePackages=9,nativeCases=native,currentVideos=movies_total,currentStrictVideoPass=strict_total,historicalFailuresRetained=True,sourceAudit=physics.artifact(OUT/'verification/source-audit.json'),deepProofs=physics.artifact(OUT/'verification/deep-proofs.json'),archive=physics.artifact(core.REPO/'pcg/archives/approved-review040-implementation-v1/manifest.json'),results=results,productionApproval=False)
 core.write(OUT/'index.json',index)
 for path in Path('/tmp').glob('review040-*.log'):
  if path.is_file()and not path.name.startswith(('review040-publish','review040-public')):shutil.copy2(path,OUT/'verification'/path.name)
 print('CURRENT_67_OF_72',index['formalAttempts'],native,movies_total,strict_total,flush=True)
if __name__=='__main__':main()
