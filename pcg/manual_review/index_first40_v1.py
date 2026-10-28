"""Build a current delivery index without rewriting any historical result."""
import copy
from pathlib import Path
from pcg.migration import core,physics,godot_package
ROOT=core.REPO/'feedback/manual-review/implementation-results/first-40-v1'

def current(row):
    n=row['reviewId'];mid=row['moduleId']
    if n in ('32','34','37','39'):
        folder=core.REPO/'pcg/manual_review/implementation/first-40-bound-v1'/mid;proof=core.read(folder/'qualification-corrected.json')['report']
    elif n in ('35','36'):
        folder=core.REPO/'pcg/manual_review/implementation'/('first-40-final-v2'if n=='35'else'first-40-final-v1')/mid;proof=core.read(folder/('qualification.json'if n=='35'else'qualification-completed.json'))['report']
    elif n=='17':
        folder=core.REPO/'pcg/manual_review/implementation/first-40-repair17-v2'/mid;proof=core.read(folder/'qualification-repaired.json')['report']
    else:
        old=core.read(ROOT.parent/'first-30-v2'/(n+'.json'));folder=core.resolve_artifact(old['module']['path']).parent;proof=old['qualificationReport']
        if n in ('02','03'):proof=physics.artifact(core.REPO/'pcg/results'/('approved-b001-'+n+'-qualified-v7/migration-physics.json'))
    return folder,proof

def main():
    rows=core.read(ROOT/'authorization/handoff.json')['rows'];results=[];total_routes=0
    for row in rows:
        n=row['reviewId'];folder,proof=current(row);doc=core.read(folder/'module.mapnote.json');report=core.read(core.resolve_artifact(proof['path']));assert report['passed'],n
        core.verify_artifacts([proof,physics.artifact(folder/'module.mapnote.json')]);assert report['contentVersion']==doc['generationContract']['contentVersion'],n
        native=godot_package.verify_package(folder/'playable');assert native['loaded']and native['passed'];total_routes+=native['canonical_cases']
        assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
        assert core.sha(core.REPO/row['sourceModule']['file'])==row['sourceModule']['sha256']
        videos=[];fresh=ROOT/'videos'/(n+'-v2')/'manifest.json'
        if fresh.exists():videos=[physics.artifact(fresh)]
        elif int(n)<=30:videos=core.read(ROOT.parent/'first-30-v2'/(n+'.json'))['videos']
        result=dict(schema='pcg/approved-design-implementation-result/v3',reviewId=n,moduleId=row['moduleId'],sourceModule=row['sourceModule'],designFile=row['designFile'],designFileSha256=row['designFileSha256'],designVersion=row['designVersion'],implementationVersion=doc['generationContract']['contentVersion'],module=physics.artifact(folder/'module.mapnote.json'),parameters=physics.artifact(folder/'parameters.json'),physicsCases=physics.artifact(folder/'physics-input-cases.json'),localTechnicalQualification='PASS',qualificationReport=proof,attempts=report['actualAttempts'],nativePlayable=dict(path=core.relative(folder/'playable'),passed=True,canonicalRoutes=native['canonical_cases'],manifest=physics.artifact(folder/'playable/godot-package.json'),verification=native),videos=videos,formalLibraryChanged=False,humanPlaytest='UNKNOWN',humanVideoObservation='UNKNOWN',productionApproval=False,unknown=['unmeasured entry states','mirror','closure combinations','full Map'],authorization=physics.artifact(ROOT/'authorization/request.json'))
        if n=='17':result['sameWorldReturn']=dict(passed=True,scope='actual A-C-A earned bridge, original actor/world/resources',freshCReturn='UNKNOWN',worldRebuilt=False)
        if n in('02','03'):result['continuedVerification']=dict(budget=physics.artifact(ROOT/'authorization/continuation-verification-budget.json'),oldFailuresPreserved=True,seedRerolls=0)
        core.write(ROOT/(n+'.json'),result);results.append(dict(reviewId=n,moduleId=row['moduleId'],status='PASS',result=physics.artifact(ROOT/(n+'.json')),routes=native['canonical_cases']))
    discards=core.read(ROOT/'authorization/handoff.json')['policy']['discardedReviewIds'];assert len(results)==21 and len(discards)==19
    core.write(ROOT/'index.json',dict(schema='pcg/approved-design-implementation-index/v3',requestedScope='reviewId 01 through 40, actual human decisions, not batch arithmetic',baseMain=core.read(ROOT/'authorization/request.json')['baseMain'],retained=21,discarded=19,qualified=21,unresolved=0,nativeCanonicalRoutes=total_routes,results=results,discardedReviewIds=discards,deletionReceipt=physics.artifact(ROOT/'deletions.json'),historicalFirst30='feedback/manual-review/implementation-results/first-30-v2/index.json',designPagesModified=False,formalCandidatePromotion=False,humanPlaytest='UNKNOWN',productionApproval=False))
    print('INDEX',len(results),'PASS',total_routes,'native routes',flush=True)
if __name__=='__main__':main()
