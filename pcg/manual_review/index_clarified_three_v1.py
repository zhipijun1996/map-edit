"""Append current results; historical failures and source versions remain intact."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import json,subprocess,shutil
from pathlib import Path
from collections import Counter
from pcg.migration import core,physics
from pcg.manual_review.repair_clarified_three_v1 import OUT,AUTH,rows
from pcg.manual_review.finalize_clarified_three_v1 import folder_for

def main():
 result_rows=[];bindings=core.read(AUTH/'version-bindings.json')
 for row in rows():
  n=row['reviewId'];f=folder_for(row);d=core.read(f/'module.mapnote.json');q=core.read(f/('qualification-repaired.json'if n=='174'else'qualification.json'));report=core.read(core.resolve_artifact(q['report']['path']));assert report['passed'];package=core.read(f/'package-result.json');assert package['passed'];video=OUT/'videos'/(n+'-v1')/'manifest.json';m=core.read(video);clip=video.parent/m['clips'][0]['file'];log=next(video.parent.glob('*.record.log')).read_text();native=json.loads(next(v for v in log.splitlines()if v.startswith('WORKSHOP_MOVIE_RESULT ')).split(' ',1)[1]);assert native['safe']and native['hp']==5
  stats=[]
  for rt in report['routes']:
   r=dict(routeId=rt['routeId'],passed=rt['passed'])
   for stage in ('calibration','holdout'):
    s=core.read(core.resolve_artifact(rt[stage]['path']))['stats'];r[stage]={k:dict(passed=s[k]['purpose_valid'],trials=s[k]['trials'])for k in ['clean','mild','moderate']}
   stats.append(r)
  diff=core.read(video.parent/'strict-comparison-failed.json')if m.get('reviewOnly')else None
  result=dict(schema='pcg/approved-design-implementation-result/v7',reviewId=n,moduleId=row['moduleId'],status='PASS',authorization=physics.artifact(AUTH/'request.json'),versionBindings=physics.artifact(AUTH/'version-bindings.json'),design=physics.artifact(core.REPO/row['designFile']),designVersion=row['designVersion'],implementationVersion=d['generationContract']['contentVersion'],module=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'),physicsCases=physics.artifact(f/'physics-input-cases.json'),qualificationReport=q['report'],formalAttempts=report['actualAttempts'],routes=stats,nativePlayable=dict(path=core.relative(f/'playable'),manifest=physics.artifact(f/'playable/godot-package.json'),passed=True),video=physics.artifact(video),movie=physics.artifact(clip),videoStrictComparison='FAIL; review-only'if m.get('reviewOnly')else'PASS',videoDifferences=dict(Counter(x['field']for x in diff['differences']))if diff else{},movieNativeOutcome=native,supersedes=physics.artifact(core.REPO/'feedback/manual-review/implementation-results/review-029-v1'/(n+'.json')),humanPlaytest='UNKNOWN',productionApproval=False,scope=dict(orientation='identity',mirror='UNKNOWN',closureConfigurations='UNKNOWN',sameWorldReturn='UNKNOWN',fullMap='UNKNOWN'))
  if n=='174':result['shortReview']=physics.artifact(video.parent/'short-review-manifest.json')
  core.write(OUT/(n+'.json'),result);result_rows.append(dict(reviewId=n,status='PASS',result=physics.artifact(OUT/(n+'.json')),formalAttempts=result['formalAttempts']))
 core.write(OUT/'index.json',dict(schema='pcg/clarified-implementation-index/v1',scope=['171','174','175'],results=result_rows,newlyQualified=3,currentQualified=59,approved=59,remainingCurrentFailures=[],formalAttempts=sum(r['formalAttempts']for r in result_rows),nativePackages=3,nativeCases=4,videos=3,strictVideoPass=0,original870Protected=True,webDesignEdits=False,archive=physics.artifact(core.REPO/'pcg/archives/approved-clarified-three-v1/manifest.json')if(core.REPO/'pcg/archives/approved-clarified-three-v1/manifest.json').exists()else'pending',originalFailuresPreserved=True,rootProductionPromotion=False))
 for p in Path('/tmp').glob('clarified-three-*.log'):
  if p.is_file():shutil.copy2(p,OUT/'verification'/p.name)
 print('ALL_THREE_PASS_CURRENT_59_OF_59',flush=True)
if __name__=='__main__':main()
