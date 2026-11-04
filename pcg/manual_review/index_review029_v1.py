"""Read current immutable proof; keep technical failure and delivery separate."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,gzip,json,hashlib,subprocess,shutil
from pathlib import Path
from collections import Counter
from pcg.migration import core,physics
from pcg.manual_review.prepare_review029_v1 import AUTH
from pcg.manual_review.finalize_review029_v1 import folder_for
OUT=AUTH.parent
NOTES={
 '171':'UNQUALIFIED: native middle trigger, two spawned original sentries and inward native collision motion implemented. Canonical both directions and native package pass; mild/moderate screen still contains actual player harm. No formal holdout run. Finite control failures do not prove impossibility.',
 '174':'DESIGN_CONFLICT: approved exit is ROCK, but support is an actual ONE_WAY_PLATFORM at [-128,310,168,24]. Static contract rejects this exact combination. Actual native wall-kick diagnostic passes after an interior right-shore staging correction. No geometry or Port surface changed; formal and native package withheld until this explicit conflict is resolved.',
 '175':'UNQUALIFIED: original native carrier Dock and mounted ShotLatch connected and observed; same carrier opens the gate. Last bounded control still misses the final boarding support, leaves the rectangle and times out. Seven distinct programs (initial + six revisions); no formal holdout run; no claim of impossible design.'}

def main():
 rows=core.read(AUTH/'handoff.json')['rows'];results=[];budget=[]
 prov=core.read('pcg/prototype/godot/source_provenance.json');mismatch=[p for p,sha in prov['files'].items()if core.sha(core.REPO/'pcg/prototype/godot'/p)!=sha];assert not mismatch
 for row in rows:
  n=row['reviewId'];f=folder_for(row);draft=core.REPO/row['outputDirectory'];versions={}
  for p in list((draft/'history').glob('*cases.json'))+[draft/'cases.json']:
   cs=core.read(p)['cases'];key=hashlib.sha256(json.dumps([c['control_plan']for c in cs],sort_keys=True).encode()).hexdigest();versions.setdefault(key,[]).append(core.relative(p))
  assert len(versions)<=7
  budget.append(dict(reviewId=n,distinctPrograms=len(versions),revisionsAfterInitial=max(0,len(versions)-1),maximumRevisions=6,programs=[dict(sha256=k,artifacts=v)for k,v in versions.items()],formalVersionLimit=1))
  result=dict(schema='pcg/approved-design-implementation-result/v6',reviewId=n,moduleId=row['moduleId'],designVersion=row['designVersion'],authorization=physics.artifact(AUTH/'request.json'),design=physics.artifact(core.REPO/row['designFile']),source=row['sourceModule'],candidate=core.relative(f if f.exists()else draft),localTechnicalQualification='UNQUALIFIED',notes=NOTES.get(n),humanPlaytest='UNKNOWN',productionApproval=False)
  if (f/'module.mapnote.json').exists():
   d=core.read(f/'module.mapnote.json');result.update(implementationVersion=d['generationContract']['contentVersion'],module=physics.artifact(f/'module.mapnote.json'),parameters=physics.artifact(f/'parameters.json'))
  qfile=f/('qualification-reanalyzed.json'if(f/'qualification-reanalyzed.json').exists()else'qualification.json')
  if qfile.exists():
   q=core.read(qfile);report=physics.verify_report(f,q['report']);assert report['passed'];result.update(localTechnicalQualification='PASS',qualificationReport=q['report'],formalAttempts=report['actualAttempts'],routes=[])
   for r in report['routes']:
    v=dict(routeId=r['routeId'],passed=r['passed'])
    for stage in ('calibration','holdout'):
     stats=core.read(core.resolve_artifact(r[stage]['path']))['stats'];v[stage]={k:dict(passed=stats[k]['purpose_valid'],trials=stats[k]['trials'])for k in ('clean','mild','moderate')}
    result['routes'].append(v)
  if n=='174':result.update(localTechnicalQualification='DESIGN_CONFLICT',staticConflict=physics.artifact(draft/'static-conflict.json'),nativeDiagnostic=physics.artifact(core.REPO/'pcg/results/approved-r029-174-canonical-static-conflict-diagnostic-v2/canonical.json'))
  if (f/'playable/godot-package.json').exists():result['nativePlayable']=dict(path=core.relative(f/'playable'),manifest=physics.artifact(f/'playable/godot-package.json'),result=core.read(f/'package-result.json'),qualification=result['localTechnicalQualification'])
  video=OUT/'videos'/ (n+'-v1')/'manifest.json'
  if video.exists():
   m=core.read(video);diff=core.read(video.parent/'strict-comparison-failed.json')if m.get('reviewOnly')else None;log=next(video.parent.glob('*.record.log')).read_text();line=next(v for v in log.splitlines()if v.startswith('WORKSHOP_MOVIE_RESULT '));native=json.loads(line.split(' ',1)[1]);assert native['safe']and native['hp']==5 and native['stable_frames']>=12
   result.update(video=physics.artifact(video),movie=physics.artifact(video.parent/m['clips'][0]['file']),videoStrictComparison='FAIL; review-only'if m.get('reviewOnly')else'PASS',videoMismatchFields=dict(Counter(v['field']for v in diff['differences']))if diff else{},nativeMovieOutcome=native)
  core.write(OUT/(n+'.json'),result);results.append(result)
 qualified=[r['reviewId']for r in results if r['localTechnicalQualification']=='PASS'];unqualified=[r['reviewId']for r in results if r['localTechnicalQualification']!='PASS'];assert len(qualified)==10 and unqualified==['171','174','175']
 core.write(OUT/'verification/revision-budget.json',budget)
 core.write(OUT/'verification/source-audit.json',dict(passed=True,engine=physics.artifact(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),engineVersion=subprocess.check_output([str(core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64'),'--version'],text=True).strip(),protectedFiles=len(prov['files']),protectedMismatches=mismatch,gameSourceCommit='12f6cb006d7119598e3235f4ca4f7323e4c9d092',designWebDiff=subprocess.check_output(['git','diff','--name-only','origin/main','--','generation/manual-review'],text=True).splitlines()))
 assert not core.read(OUT/'verification/source-audit.json')['designWebDiff']
 index=dict(schema='pcg/approved-implementation-refresh-index/v2',baseMain=core.read(AUTH/'request.json')['baseMain'],scopeIds=[r['reviewId']for r in rows],newlyQualified=qualified,notFullyQualified=unqualified,totalApproved=59,totalCurrentQualified=56,retained157TopPlusOneBlock=True,deletedThisRefresh=17,totalDeleted=57,currentActiveTemplates=len(core.read(core.ACTIVE/'catalog.json')['modules']),pendingUnapproved=core.read(AUTH/'handoff.json')['policy']['unapprovedReviewIds'],formalAttempts=sum(r.get('formalAttempts',0)for r in results),nativePackages=sum('nativePlayable'in r for r in results),videos=sum('video'in r for r in results),videoStrictPass=sum(r.get('videoStrictComparison')=='PASS'for r in results),results=[dict(reviewId=r['reviewId'],status=r['localTechnicalQualification'],result=physics.artifact(OUT/(r['reviewId']+'.json')))for r in results],sourceAudit=physics.artifact(OUT/'verification/source-audit.json'),revisionBudget=physics.artifact(OUT/'verification/revision-budget.json'),productionApproval=False)
 core.write(OUT/'index.json',index)
 for p in Path('/tmp').glob('review029-*.log'):
  if p.is_file():shutil.copy2(p,OUT/'verification'/p.name)
 print('INDEX',qualified,unqualified,index['formalAttempts'],index['nativePackages'],index['videos'],flush=True)
if __name__=='__main__':main()
