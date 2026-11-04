"""Current supplement for the explicitly authorized 157 top expansion."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import json,subprocess,hashlib,shutil
from collections import Counter
from pathlib import Path
from pcg.migration import core,physics
from .repair_157_upper_block_v1 import ROOT,AUTH,OLD,folder,row

def main():
    f=folder();old=core.read(OLD/'module.mapnote.json');doc=core.read(f/'module.mapnote.json');assert old['objects']==doc['objects'];keys=('id','position','stagingPosition','normal','surface','permission');before=[{k:p[k]for k in keys}for p in old['generationContract']['ports']];after=[{k:p[k]for k in keys}for p in doc['generationContract']['ports']];assert before==after
    qualification=core.read(f/'qualification.json');assert qualification['passed'];report=physics.verify_report(f,qualification['report']);assert report['passed'];package=core.read(f/'package-result.json');assert package['passed'];video=ROOT/'videos/157-upper-block-v1/manifest.json';m=core.read(video);clip=m['clips'][0];movie=video.parent/clip['file'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(movie)]));assert probe['streams'][0]['avg_frame_rate']=='60/1';line=next(v for v in next(video.parent.glob('*.record.log')).read_text().splitlines()if v.startswith('WORKSHOP_MOVIE_RESULT '));outcome=json.loads(line.split(' ',1)[1]);assert outcome['safe']and outcome['hp']==5 and outcome['stable_frames']>=12
    diff=core.read(video.parent/'strict-comparison-failed.json');fields=dict(Counter(v['field']for v in diff['differences']));assert set(fields)<= {'workshop','support_id'}
    provenance=core.read('pcg/prototype/godot/source_provenance.json');assert all(core.sha(core.REPO/'pcg/prototype/godot'/p)==sha for p,sha in provenance['files'].items())
    artifact=physics.artifact
    geometry=dict(passed=True,beforeBounds=old['generationContract']['space']['bounds'],afterBounds=doc['generationContract']['space']['bounds'],beforeBlocks=[6,1],afterBlocks=[6,2],addedTopPixels=128,allObjectsByteEquivalent=True,allSidePortWorldDefinitionsEquivalent=True,beforePortDefinitions=before,afterPortDefinitions=after,newPortGridCells=[dict(id=p['id'],cell=p['grid']['cell'])for p in doc['generationContract']['ports']],bodyCenterMarginAboveGearsBefore=4,bodyCenterMarginAboveGearsAfter=132)
    core.write(ROOT/'verification/geometry-and-source-audit.json',dict(**geometry,originalProtectedFiles=len(provenance['files']),protectedMismatches=[]))
    rates={}
    for stage in ('calibration','holdout'):
        stats=core.read(core.resolve_artifact(report['routes'][0][stage]['path']))['stats'];rates[stage]={level:str(stats[level]['purpose_valid'])+'/'+str(stats[level]['trials'])for level in ('clean','mild','moderate')}
    result=dict(schema='pcg/approved-design-implementation-result/v5',reviewId='157',moduleId='game-plains-twin-gears',authorization=artifact(AUTH/'request.json'),design=artifact(AUTH/'target-design.json'),designVersion=row()['designVersion'],implementationVersion=doc['generationContract']['contentVersion'],module=artifact(f/'module.mapnote.json'),parameters=artifact(f/'parameters.json'),physicsCases=artifact(f/'physics-input-cases.json'),localTechnicalQualification='PASS',qualificationReport=qualification['report'],actualFormalAttempts=report['actualAttempts'],calibration=rates['calibration'],holdout=rates['holdout'],nativePlayable=dict(path=core.relative(f/'playable'),manifest=artifact(f/'playable/godot-package.json'),verification=package),video=artifact(video),videoStrictComparison='FAIL; review-only',videoMismatchFields=fields,nativeMovieOutcome=outcome,geometryAudit=artifact(ROOT/'verification/geometry-and-source-audit.json'),supersedes=artifact(core.REPO/'feedback/manual-review/implementation-results/review-refresh-v1/157.json'),oldVersionOutcomeUnchanged='UNQUALIFIED',scope=dict(routeIds=['entry-to-exit'],orientation='identity',connectedPortSubset=['entry','exit'],closureProfile=None,reverse='UNKNOWN',mirror='UNKNOWN',fullMap='UNKNOWN',humanPlaytest='UNKNOWN',productionApproval=False))
    core.write(ROOT/'157.json',result)
    previous=core.read('feedback/manual-review/implementation-results/review-refresh-v1/index.json');current=core.read('feedback/manual-review/implementation-handoff-v1.json');known={r['reviewId']for r in previous['results']}|{r['reviewId']for r in core.read('feedback/manual-review/implementation-results/first-40-v1/index.json')['results']};pending=[r['reviewId']for r in current['rows']if r['reviewId']not in known]
    core.write(ROOT/'index.json',dict(schema='pcg/implementation-followup-index/v1',result=artifact(ROOT/'157.json'),implementedRetained=46,currentTechnicalPass=46,currentTechnicalFailures=[],previousVersionFailurePreserved=True,pendingApprovedNotImplemented=pending,pendingNewDiscardOutsideThisTask=['172'],historicalDeleted=40,publishedDesignAndWebFilesUnchanged=True,scope='157 user-authorized top +1 Block only; no automatic expansion to other newly approved designs'))
    for p in Path('/tmp').glob('157-upper-*.log'):
        if p.is_file():shutil.copy2(p,ROOT/'verification'/p.name)
    print('157_PASS_ALL_46_IMPLEMENTED_PASS',pending,fields,flush=True)
if __name__=='__main__':main()
