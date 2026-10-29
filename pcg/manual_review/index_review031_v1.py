"""Publish current statuses without rewriting historical failures."""
import json,shutil
from pathlib import Path
from collections import Counter
from pcg.migration import core,physics
from .prepare_review031_v1 import OUT,AUTH,rows
from .finalize_review031_v1 import folder_for
def main():
 results=[]
 for row in sorted(rows(),key=lambda r:int(r['reviewId'])):
  n=row['reviewId'];result=dict(schema='pcg/approved-design-implementation-result/v8',reviewId=n,moduleId=row['moduleId'],design=physics.artifact(core.REPO/row['designFile']),designVersion=row['designVersion'],authorization=physics.artifact(AUTH/'request.json'),humanPlaytest='UNKNOWN',productionApproval=False)
  if n=='196':result.update(status='DESIGN_CONFLICT',conflict=physics.artifact(OUT/'196-design-conflict.json'),formalAttempts=0,godot='NOT_RUN: approved BOTTOM AIR INOUT violates Foundation',noPhysicsImpossibilityClaim=True)
  else:
   f=folder_for(row);doc=core.read(f/'module.mapnote.json');q=core.read(f/('qualification-reanalyzed.json'if n=='197'else'qualification.json'));r=core.read(core.resolve_artifact(q['report']['path']));assert r['passed'];p=core.read(f/'package-result.json');assert p['passed'];stats=[]
   for route in r['routes']:
    v=dict(routeId=route['routeId'],passed=route['passed'])
    for stage in ['calibration','holdout']:
     s=core.read(core.resolve_artifact(route[stage]['path']))['stats'];v[stage]={k:dict(passed=s[k]['purpose_valid'],trials=s[k]['trials'])for k in ['clean','mild','moderate']}
    stats.append(v)
   movies=[]
   for route in stats:
    video=OUT/'videos'/(n+'-'+route['routeId']+('-v2'if n=='198'else'-v1'))/'manifest.json';m=core.read(video);diff=core.read(video.parent/'strict-comparison-failed.json')if m.get('reviewOnly')else None;log=next(video.parent.glob('*.record.log')).read_text();native=json.loads(next(v for v in log.splitlines()if v.startswith('WORKSHOP_MOVIE_RESULT ')).split(' ',1)[1]);assert native['safe']and native['hp']==5
    movies.append(dict(routeId=route['routeId'],manifest=physics.artifact(video),movie=physics.artifact(video.parent/m['clips'][0]['file']),durationSeconds=m['clips'][0]['duration'],comparison='FAIL; review-only'if m.get('reviewOnly')else'PASS',differenceFields=dict(Counter(v['field']for v in diff['differences']))if diff else{},nativeOutcome=native))
   result.update(status='PASS',implementationVersion=doc['generationContract']['contentVersion'],module=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),physicsCases=physics.artifact(f/'physics-input-cases.json'),qualificationReport=q['report'],formalAttempts=r['actualAttempts'],routes=stats,nativePlayable=dict(path=core.relative(f/'playable'),manifest=physics.artifact(f/'playable/godot-package.json'),result=physics.artifact(f/'package-result.json'),passed=True),videos=movies,scope=dict(orientation='identity',mirror='UNKNOWN',closureConfigurations='UNKNOWN',fullMap='UNKNOWN'))
   if n=='197':result['originalFailure']=q['originalFailure'];result['newPhysicsAttemptsForReanalysis']=0
   if n=='200':result['sameWorldReturn']=physics.artifact(OUT/'verification/200-same-world-witness.json')
  core.write(OUT/(n+'.json'),result);results.append(dict(reviewId=n,status=result['status'],result=physics.artifact(OUT/(n+'.json')),formalAttempts=result['formalAttempts']))
 index=dict(schema='pcg/approved-implementation-refresh-index/v3',baseMain=core.read(AUTH/'request.json')['baseMain'],scopeIds=[r['reviewId']for r in results],newlyQualified=['197','198','200'],notFullyQualified=['196'],totalApproved=63,totalCurrentQualified=62,retained157TopPlusOneBlock=True,retained171174175Clarifications=True,deletedThisRefresh=3,totalDeleted=60,currentActiveTemplates=len(core.read(core.ACTIVE/'catalog.json')['modules']),pendingUnapproved=['202','204'],formalAttempts=sum(r['formalAttempts']for r in results),nativePackages=3,nativeCases=4,currentVideos=4,currentStrictVideoPass=1,historicalVideoFailureRetained=True,sourceAudit=physics.artifact(OUT/'verification/source-audit.json'),deepProofs=physics.artifact(OUT/'verification/deep-proofs.json'),archive=physics.artifact(core.REPO/'pcg/archives/approved-review031-implementation-v1/manifest.json'),results=results,productionApproval=False)
 core.write(OUT/'index.json',index)
 for p in Path('/tmp').glob('review031-*.log'):
  if p.is_file()and not p.name.startswith(('review031-publish','review031-public')):shutil.copy2(p,OUT/'verification'/p.name)
 print('CURRENT_62_OF_63;196_DESIGN_CONFLICT',flush=True)
if __name__=='__main__':main()
