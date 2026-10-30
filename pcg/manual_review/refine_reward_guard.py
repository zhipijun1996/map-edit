"""New bounded diagnostic cycle: remove a redundant arrival shot and clear the actual Port stage.

The prior two-geometry/80-control cycle remains failed for the high route. No threshold or past budget changes.
"""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pathlib import Path
import copy,shutil,json
from pcg.migration import core,physics,godot_package
from pcg.prototype.factory.core.quality import digest
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
ROOT=core.REPO;PARENT=ROOT/'pcg/manual_review/batch-001/revision-002';ID='b31-n12-three-side-port-interface0';OUT=PARENT.with_name('revision-003')/ID

def run():
 if OUT.exists():raise ValueError('new_cycle_already_exists')
 OUT.mkdir(parents=True);doc=core.read(PARENT/ID/'module.mapnote.json');cs=core.read(PARENT/ID/'cases.json')['cases'];old=doc['generationContract']['contentVersion']
 guard=next(o for o in doc['objects']if o.get('sourceId')=='review-cache-sentry');guard['x']=384
 cs[0]['control_plan']=[v for v in cs[0]['control_plan']if not(v['op']=='shoot'and not v.get('aim_cell'))]
 for c in cs:
  c.update(copy.deepcopy(godot_package.content_from_objects(doc)));c.pop('recorded_frames',None);c['human_review_revision']['id']='batch-001/revision-003'
 g=doc['generationContract'];g['generation']['humanReviewRevision'].update(id='batch-001/revision-003',previousCandidateVersion=old,newCycleReason='Prior high route reached reward but redundant final upward shot violated body ownership; right-position guard also occupied B staging. New hypothesis removes that shot and moves the same guard to the left edge of the same right bank.',controlProgramsSha256=digest([c['control_plan']for c in cs]))
 core.write(OUT/'module.mapnote.json',doc);core.write(OUT/'cases.json',dict(cases=cs));core.contract(OUT/'module.mapnote.json',refresh=True)
 eng,cs,authors=physics._engine(OUT,'manual-review-b001-r3-03-canonical',physics.FULL_PROTOCOL)
 core.write(eng.out/'protocol.json',dict(maximumCases=2,geometryRevisionsThisCycle=1,maximumGeometryRevisionsThisCycle=1,selection='Single explicit repaired policy per direction; no parameter search',previousCycle='revision-002 high route remains failed after its fixed 80-control budget',qualityThresholdsUnchanged=True,calibration='NOT_RUN',holdout='NOT_RUN'))
 diagnostics=[];recordings=[]
 for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'canonical')for c in cs],'canonical')):
  q=checked_purpose(authors[i],c,r);diagnostics.append(dict(routeId=cs[i]['route_spec']['id'],diagnosticPurposePassed=q['ok'],reasons=q['reasons'],rawRun='manual-review-b001-r3-03-canonical',evidence=e,rawInputCaseId=r['id']));recordings.append(physics._recording(cs[i],r))
  route=next(v for v in g['routes']if v['id']==cs[i]['route_spec']['id']);o=next(o for o in doc['objects']if o['id']==route['pathObjectId']);o['points']=[dict(x=f['x'],y=f['y'])for f in r['frames']];route['resourcePressure'].update(observedShots=r.get('shots'),observedJumps=r.get('jumps'),rewardGrant=r.get('workshop',{}).get('coins',0),phaseWaits=[v for v in cs[i]['control_plan']if v['op']=='wait'])
 core.write(eng.out/'canonical-check.json',dict(rows=diagnostics,technicalAdmission=False));print(json.dumps(diagnostics),flush=True)
 core.write(OUT/'module.mapnote.json',doc);core.write(OUT/'cases.json',dict(cases=recordings));core.contract(OUT/'module.mapnote.json',refresh=True)
 cv=core.read(OUT/'module.mapnote.json')['generationContract']['contentVersion'];status=dict(schema='pcg/manual-review-candidate-status/v1',reviewId='03',contentVersion=cv,diagnostics=diagnostics,calibration='NOT_RUN',holdout='NOT_RUN',humanApprovalOfRevision='UNKNOWN',productionApproval=False);core.write(OUT/'review-status.json',status)
 receipt=core.read(PARENT/'feedback.json');row=receipt['rows'][2];row.update(candidate=core.relative(OUT),contentVersion=cv,revision='batch-001/revision-003',canonicalDiagnostics=diagnostics);core.write(PARENT/'feedback.json',receipt)
 if all(v['diagnosticPurposePassed']for v in diagnostics):
  r=physics.run_clean(OUT,'manual-review-b001-r3-bound-03');p=core.read(PARENT/'final-preflight.json');p['rows'].append(dict(reviewId='03',passed=r['passed'],attempts=r['actualAttempts'],report='pcg/results/manual-review-b001-r3-bound-03/clean-preflight.json'));p['rows'].sort(key=lambda r:r['reviewId']);core.write(PARENT/'final-preflight.json',p);print(json.dumps(dict(preflightPassed=r['passed'],attempts=r['actualAttempts'])),flush=True)
 package=OUT/'playable-final';godot_package.compile_package(OUT/'module.mapnote.json',OUT/'cases.json',package,stable_id=ID)
 try:
  result=godot_package.run_package_validation(package);p=core.read(PARENT/'native-samples.json');p['rows'][2].update(status='CANONICAL_NATIVE_REPLAY_PASSED',nativeReplay=result);core.write(PARENT/'native-samples.json',p);print(json.dumps(dict(nativeReplay=result['passed'])),flush=True)
 except Exception as e:print(json.dumps(dict(nativeReplay=False,conflict=str(e))),flush=True)
if __name__=='__main__':run()
