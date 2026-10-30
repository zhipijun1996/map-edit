"""Verify and index the reviewed scope without promoting isolated candidates."""
import argparse,subprocess
from pathlib import Path
from pcg.migration import core,physics,godot_package
from . import finalize_first30_v1 as v1,finalize_first30_v2 as v2

OUT=core.REPO/'feedback/manual-review/implementation-results/first-30-v2'

def folder_for(row):
    n=row['reviewId']
    if n=='01':return core.REPO/'pcg/manual_review/implementation/first-30-v2'/row['moduleId']
    if n in('02','03'):return core.REPO/'pcg/manual_review/implementation/first-30-v4'/row['moduleId']
    if n in('04','05'):return core.REPO/'pcg/manual_review/implementation/batch-001'/row['moduleId']
    return(v2 if n in('07','10')else v1).folder_for(row)

def main():
    rows=[]
    for row in core.read(v1.AUTH/'handoff.json')['rows']:
        n=row['reviewId'];folder=folder_for(row);doc=core.read(folder/'module.mapnote.json');package=folder/'playable'
        if n in('04','05'):
            old=core.read('feedback/manual-review/implementation-results/batch-001/'+n+'.json');package=(core.REPO/old['nativePlayable']).parent;proof=old['rawReport']
        elif n=='01':proof=physics.artifact(core.REPO/'pcg/results/approved-b001-01-qualified-v5/migration-physics-approved-external-apron-scope-v1.json')
        elif n in('07','12'):proof=core.read(folder/'qualification-reanalysis.json')['report']
        elif n=='23':proof=core.read(folder/'qualification-repaired.json')['report']
        elif n in('02','03'):proof=None
        else:proof=core.read(folder/'qualification.json')['report']
        native=godot_package.verify_package(package,require_loaded=True);assert native['passed']
        status='UNKNOWN'if n in('02','03')else'FAIL'if n=='17'else'PASS'
        if status=='PASS':physics.verify_report(folder,proof)
        assert core.sha(core.REPO/row['designFile'])==row['designFileSha256']
        videos=[]
        if n in('04','05'):videos=[old['video']]
        else:
            for p in sorted((OUT/'videos').glob(n+'-*/manifest.json')):videos.append(physics.artifact(p))
        item=dict(schema='pcg/approved-design-implementation-result/v2',reviewId=n,moduleId=row['moduleId'],designVersion=row['designVersion'],designFile=row['designFile'],designFileSha256=row['designFileSha256'],implementationVersion=doc['generationContract']['contentVersion'],module=physics.artifact(folder/'module.mapnote.json'),parameters=physics.artifact(folder/'parameters.json'),physicsCases=physics.artifact(folder/'physics-input-cases.json'),candidateStatus='IMPLEMENTED_PLAYABLE_CANDIDATE',localTechnicalQualification=status,qualificationReport=proof,nativePlayable=dict(path=core.relative(package),passed=True,canonicalRoutes=native['canonical_cases'],manifest=physics.artifact(package/'godot-package.json')),videos=videos,formalLibraryChanged=False,humanVideoObservation='UNKNOWN',humanPlaytest='UNKNOWN',productionApproval=False,unknown=['unmeasured entry states','closure combinations','mirror','full Map'])
        if n in('02','03'):
            item.update(calibration=physics.artifact(core.REPO/'pcg/results'/('approved-b001-'+n+'-repair-final-calibration-v7/calibration.json')),independentHoldout='NOT_RUN_FOR_FINAL_REPAIR_BUDGET_PENDING',previousFailuresPreserved=['approved-b001-'+n+'-qualified-v5','approved-b001-'+n+'-qualified-v6'],budgetRequest=physics.artifact(OUT/'proposed-extra-holdout-budget.json'))
        if n=='17':item.update(sameWorldReturn=dict(passed=True,proof=physics.artifact(core.REPO/'pcg/results/approved-b001-first30-17-earned-return-final-v1/canonical.json'),native=physics.artifact(folder/'earned-loop-package-result.json'),playable=core.relative(folder/'earned-loop-playable'),worldRebuilt=False,freshCQualification='UNKNOWN'),unresolved='The control strategy did not meet perturbation thresholds; no impossibility or design-conflict claim.')
        item.update(sourceModule=row['sourceModule'],authorization=physics.artifact(v1.AUTH/'request.json'),baseMain=core.read(v1.AUTH/'request.json')['baseMain'])
        core.write(OUT/(n+'.json'),item);rows.append(item);print(n,status,'native',native['canonical_cases'],flush=True)
    provenance=core.read('pcg/prototype/godot/source_provenance.json');bad=[p for p,sha in provenance['files'].items()if core.sha(core.REPO/'pcg/prototype/godot'/p)!=sha];assert not bad
    deleted=core.read(OUT/'deletions.json');catalog=core.read('modules/catalog.json');assert len(catalog['modules'])==210
    for entry in deleted.get('deleted',deleted.get('rows',[])):
        if isinstance(entry,dict)and'moduleId'in entry:assert not(core.REPO/'modules'/entry['moduleId']).exists()
    changed=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation/manual-review','feedback/manual-review/implementation-handoff-v1.json','feedback/manual-review/received-design-decisions-v1.json'],cwd=core.REPO,text=True);assert not changed
    counts={status:sum(r['localTechnicalQualification']==status for r in rows)for status in ('PASS','FAIL','UNKNOWN')}
    index=dict(schema='pcg/approved-first30-delivery/v2',baseMain='2ccd4ea5',authorization=physics.artifact(v1.AUTH/'request.json'),keep=15,deleted=15,scope='first 30 reviewed entries only; keep implementations isolated, approved discards physically deleted',localTechnicalQualification=counts,playableCandidates=15,nativeRoutes=sum(r['nativePlayable']['canonicalRoutes']for r in rows),protectedGameFiles=len(provenance['files']),protectedGameMismatches=bad,currentCatalogTemplates=210,designAndReviewWebFilesChanged=False,rows=[physics.artifact(OUT/(r['reviewId']+'.json'))for r in rows],deletions=physics.artifact(OUT/'deletions.json'),newIndependentHoldoutForFinal02And03=False,humanPlaytest='UNKNOWN',productionApproval=False)
    if (core.REPO/'pcg/archives/approved-first30-implementation-v2/manifest.json').exists():index['archive']=physics.artifact(core.REPO/'pcg/archives/approved-first30-implementation-v2/manifest.json')
    index['verification']=[physics.artifact(p)for p in sorted((OUT/'verification').iterdir())if p.is_file()]
    core.write(OUT/'index.json',index)

if __name__=='__main__':main()
