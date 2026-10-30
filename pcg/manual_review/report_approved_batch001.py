"""Read-only synthesis of exact-version evidence; never grants library admission."""
from pathlib import Path
from pcg.migration import core, physics, godot_package
from .implement_approved_batch001 import verify_handoff, QUEUE

OUT=core.REPO/'feedback/manual-review/implementation-results/batch-001'


def main():
    entries=[]
    for row in verify_handoff()['rows']:
        rid=row['reviewId'];folder=core.REPO/row['outputDirectory'];doc=core.read(folder/'module.mapnote.json')
        canonical=core.REPO/'pcg/results'/('approved-b001-'+rid+'-canonical-v2');observed=core.read(canonical/'canonical.json')
        run=core.REPO/'pcg/results'/('approved-b001-'+rid+'-qualified-'+('v2' if rid=='01' else 'v3'))
        qualification=core.read(run/'migration-physics.json');routes=[]
        for i,route in enumerate(qualification['routes']):
            cal=core.read(core.REPO/route['calibration']['path'])
            held=core.read(core.REPO/route['holdout']['path']) if isinstance(route['holdout'],dict) else None
            rates=lambda d:{k:dict(passed=v['purpose_valid'],trials=v['trials'],rate=v['rate']) for k,v in d['stats'].items()}
            routes.append(dict(routeId=route['routeId'],fromPort=doc['generationContract']['routes'][i]['from'],toPort=doc['generationContract']['routes'][i]['to'],
                canonical='PASS' if observed['rows'][i]['check']['ok'] else 'FAIL',
                qualification='UNKNOWN_INVALID_BUDGET' if rid=='01' else 'PASS' if route['passed'] else 'FAIL',
                calibration=rates(cal),holdout=rates(held) if held else 'NOT_RUN',
                actualEntry=observed['rows'][i]['entrySnapshot'],observedExit=observed['rows'][i]['observedExit'],
                actualShots=observed['rows'][i]['shots'],actualJumps=observed['rows'][i]['jumps'],durationSeconds=observed['rows'][i]['seconds'],
                failures=sorted({s for r in cal['rows'] for s in r['purpose']['reasons']})))
        if rid=='01':
            audit=core.REPO/'pcg/results/approved-b001-01-boundary-audit-v3';bound=core.read(audit/'boundary-reanalysis.json')
            probes=bound['reanalysed']+bound['newIngress'];counters=core.read(audit/'counterexamples.json')
        else:
            probes=core.read(core.REPO/qualification['probes']['path']);counters=core.read(core.REPO/qualification['counterexamples']['path'])
        version='v3' if rid in ('03','05') else 'v2';video=OUT/'videos'/(rid+'-'+version);manifest=core.read(video/'manifest.json')
        result=dict(schema='pcg/approved-design-implementation-result/v1',reviewId=rid,moduleId=row['moduleId'],
            sourceMain='fd7120bee00716121d5db733f66b1946479a4af0',authorization=physics.artifact(QUEUE),
            designFile=row['designFile'],designFileSha256=row['designFileSha256'],designVersion=row['designVersion'],
            implementationVersion=doc['generationContract']['contentVersion'],candidateStatus='IMPLEMENTED_PLAYABLE_CANDIDATE',
            localTechnicalQualification='UNKNOWN_INVALID_BUDGET' if rid=='01' else 'PASS' if qualification['passed'] else 'FAIL',
            module=physics.artifact(folder/'module.mapnote.json'),parameters=physics.artifact(folder/'parameters.json'),
            canonicalCases=physics.artifact(folder/'cases.json'),physicsCases=physics.artifact(folder/'physics-input-cases.json'),
            metadataReconciliation=physics.artifact(folder/'metadata-reconciliation.json'),
            sourceBinding=physics.artifact(run/'source_binding.json'),rawReport=physics.artifact(run/'migration-physics.json'),
            nativePlayable=core.relative(folder/'playable/demo.tscn'),nativeValidation=godot_package.verify_package(folder/'playable'),
            routes=routes,directedMatrix=[dict(fromPort=r['from'],toPort=r['to'],status=next((v['qualification'] for v in routes if v['fromPort']==r['from'] and v['toPort']==r['to']),'UNKNOWN')) for r in doc['generationContract']['relations']],
            boundaries=dict(passed=sum(v['check']['passed'] for v in probes),total=len(probes),scope='local 64px ground64 aperture at offsets -2/0/+2, continuous exit, entry docking; explicit test-only neighbor floor; no terrain exported'),
            counters=dict(total=len(counters),originalFlags=sum(v['adjudication']['invalidates_design'] for v in counters),scope='Original classifier unchanged; all actual alternatives and failures retained'),
            video=dict(manifest=physics.artifact(video/'manifest.json'),file=physics.artifact(next(video.glob('*.mp4'))),strict=not manifest.get('reviewOnly',False),coverage='one representative route, not all directions'),
            reproduction=dict(bootstrap='python3 -m pcg.manual_review.bootstrap_approved_batch001',play='python3 -m pcg.manual_review.play_approved_batch001 '+rid,
                replay='python3 -m pcg.manual_review.play_approved_batch001 '+rid+' --replay',restoreRaw='python3 pcg/tools/restore_archive.py approved-designs-batch001-implementation-v1 --extract'),
            unknown=['uncertified partial-port closures','mirror/corner configurations','arbitrary ingress resources or phase','minimum abilities','full Map','human difficulty'],
            humanVideoObservation='UNKNOWN',humanPlaytest='UNKNOWN',productionApproval=False,formalLibraryChanged=False)
        if rid=='01':result['qualificationException']=dict(originalAttempts=900,selectedProtocolMaximum=350,status='INVALID_BUDGET_PRESERVED',
            laterAdditionalCases=84,newIndependentHoldout=False,observedAll12RouteRatesPass=True,
            counterFlags='3 ground-preopen C-origin attempts leave the rectangle and cost an additional real shot and time; not certified internal alternatives; original rejection flags retained.')
        if rid=='02':result['sameWorldReturn']=physics.artifact(core.REPO/'pcg/results/approved-b001-02-same-world-return-v2/return-check.json')
        core.write(OUT/(rid+'.json'),result);entries.append(dict(reviewId=rid,implementationVersion=result['implementationVersion'],status=result['localTechnicalQualification'],result=physics.artifact(OUT/(rid+'.json'))))
    core.write(OUT/'index.json',dict(schema='pcg/approved-design-implementation-results/v1',rows=entries,scope=['01','02','03','04','05'],
        nativePlayableRoutes=21,inputSmokeModules=5,canonicalRoutesPassed=21,technicalPassModules=['04','05'],
        regularQualityFailures=['02: reward-outbound','03: high-investment'],invalidQualifierModules=['01'],
        strictRepresentativeVideos=3,reviewOnlyRepresentativeVideos=2,
        rawArchive=physics.artifact(core.REPO/'pcg/archives/approved-designs-batch001-implementation-v1/manifest.json'),
        snapshot=physics.artifact(OUT/'authorization/source.json'),formalLibraryChanged=False,designWebpageChanged=False,productionApproval=False))


if __name__=='__main__':main()
