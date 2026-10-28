"""Index only completed existing evidence; never starts simulation or holdout."""
from pcg.migration import core,physics
from .probe_review_refresh_v1 import AUTH
ROOT=AUTH.parent

def main():
 rows=[];request=core.read(AUTH/'request.json');old=core.read('feedback/manual-review/implementation-results/first-40-v1/index.json')
 for row in sorted(core.read(AUTH/'handoff.json')['rows'],key=lambda r:int(r['reviewId'])):
  n=row['reviewId'];version='v2'if n in('140','154')else'v1';folder=core.REPO/('pcg/manual_review/implementation/review-refresh-final-'+version)/row['moduleId'];doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'physics-input-cases.json')['cases'];package=core.read(folder/'package-result.json');assert package['passed'];qualified=n!='157'
  if qualified:
   proof=core.read(folder/'qualification-continuation-v2.json')['report'];report=physics.verify_report(folder,proof);assert report['passed'];attempts=report['actualAttempts']
  else:proof=None;attempts=0
  video=ROOT/'videos'/(n+('-recovery-v1'if n in('122','154','157','159')else'-v1'))/'manifest.json';core.verify_artifacts([physics.artifact(video)])
  result=dict(schema='pcg/approved-design-implementation-result/v4',reviewId=n,moduleId=row['moduleId'],sourceModule=row['sourceModule'],designFile=row['designFile'],designFileSha256=row['designFileSha256'],designVersion=row['designVersion'],implementationVersion=doc['generationContract']['contentVersion'],module=physics.artifact(folder/'module.mapnote.json'),parameters=physics.artifact(folder/'parameters.json'),preparationParameters=physics.artifact(core.REPO/row['outputDirectory']/'parameters.json'),physicsCases=physics.artifact(folder/'physics-input-cases.json'),localTechnicalQualification='PASS'if qualified else'UNQUALIFIED',qualificationReport=proof,attempts=attempts,nativePlayable=dict(path=core.relative(folder/'playable'),passed=True,canonicalRoutes=len(cases),manifest=physics.artifact(folder/'playable/godot-package.json'),verification=package,routeQualification='PASS'if qualified else'UNQUALIFIED; fixed authored initial phase only'),videos=[physics.artifact(video)],designGeometryChanged=False,orientation='identity',closedPorts=[],closureCombinations='UNKNOWN',mirror='UNKNOWN',fullMap='UNKNOWN',humanPlaytest='UNKNOWN',productionApproval=False)
  if n=='157':result.update(reason='Fixed-phase clean input succeeds and loads natively, but random phase/noise calibration screen fails; 4px center corridor above each large gear. No formal holdout was consumed.',implementationFeedback=physics.artifact(ROOT/'design-feedback/157.json'))
  core.write(ROOT/(n+'.json'),result);rows.append(dict(reviewId=n,moduleId=row['moduleId'],status=result['localTechnicalQualification'],result=physics.artifact(ROOT/(n+'.json')),routes=len(cases)));print(n,result['localTechnicalQualification'],flush=True)
 qualified=sum(r['status']=='PASS'for r in rows);index=dict(schema='pcg/approved-design-implementation-index/v4',baseMain=request['baseMain'],branch='content/review-first30-implementation',refreshRetained=len(rows),refreshQualified=qualified,refreshUnqualified=len(rows)-qualified,refreshDiscarded=len(request['discardIds']),refreshNativeCanonicalRoutes=sum(r['routes']for r in rows),previousEvidence=physics.artifact(ROOT.parent/'first-40-v1/index.json'),previousQualified=old['qualified'],totalRetained=old['retained']+len(rows),totalQualified=old['qualified']+qualified,totalDiscarded=old['discarded']+len(request['discardIds']),pendingDesignApproval=request['pendingIds'],results=rows,retainedCandidatesOnly=True,designPagesChanged=False,productionApproval=False)
 core.write(ROOT/'index.json',index)
if __name__=='__main__':main()
