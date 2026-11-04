"""Bind diagnostic controls/trajectories to the five edited review drafts; never admit them."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pathlib import Path
import copy,gzip,json,shutil
from pcg.migration import core,physics
ROOT=core.REPO;OUT=ROOT/'pcg/manual_review/batch-001/revision-002'
def raw_case(run,evidence):
 p=ROOT/'pcg/results'/run/evidence['output'];return json.loads(gzip.decompress(p.read_bytes()))['results'][evidence['index']]
def finalize():
 receipt=core.read(OUT/'feedback.json');archive=OUT/'before-policy-binding'
 if archive.exists():raise ValueError('final_policy_already_bound')
 for row in receipt['rows']:
  folder=ROOT/row['candidate'];backup=archive/row['moduleId'];backup.mkdir(parents=True)
  for name in ('module.mapnote.json','cases.json'):shutil.copy2(folder/name,backup/name)
  d=core.read(folder/'module.mapnote.json');cs=core.read(folder/'cases.json')['cases'];observed=[]
  for j,c in enumerate(cs):
   rid=row['reviewId'];selected=None
   if rid=='01':
    if j==3:
     run='manual-review-b001-r2-01-policy-final';v=core.read(ROOT/'pcg/results'/run/'selected.json')['selected'][c['route_spec']['id']];c=v['case'];e=v['evidence'];selected=True
    else:run='manual-review-b001-r2-01-canonical';e=core.read(ROOT/'pcg/results'/run/'canonical-check.json')['rows'][j]['evidence'];selected=True
   elif rid=='03'and j==1:
    run='manual-review-b001-r2-03-policy-final';v=core.read(ROOT/'pcg/results'/run/'selected.json')['selected'][c['route_spec']['id']];c=v['case'];e=v['evidence'];selected=True
   elif rid=='03'and j==0:
    run='manual-review-b001-r2-03-policy-final';entry=next(v for v in core.read(ROOT/'pcg/results'/run/'selected.json')['checks']if v['reasons']==['actual_body_left_frozen_Block_ownership','actual_body_outside_foundation_rectangle']);e=entry['evidence'];input_data=core.read(ROOT/'pcg/results'/run/'physics'/(e['batch']+'.input.json'))['cases'];c=input_data[e['index']];c['id']=cs[j]['id'];selected=False
   elif rid=='02':run='manual-review-b001-r2-02-canonical';e=core.read(ROOT/'pcg/results'/run/'canonical-check.json')['rows'][j]['evidence'];selected=j==1
   else:
    run='manual-review-b001-r1-'+rid;report=core.read(ROOT/'pcg/results'/run/'clean-preflight.json');e=report['routes'][j]['evidence'];selected=True
   raw=raw_case(run,e)
   for k in ('module_sha256','noise'):c.pop(k,None)
   c['human_review_revision']['id']='batch-001/revision-002';c['recorded_frames']=[dict(frame=f['frame'],axis=f['axis'],requested=f['requested'])for f in raw['frames']];cs[j]=c
   r=next(v for v in d['generationContract']['routes']if v['id']==c['route_spec']['id']);o=next(o for o in d['objects']if o['id']==r['pathObjectId']);o['points']=[dict(x=f['x'],y=f['y'])for f in raw['frames']];o['note']='实际 Godot 诊断轨迹；未获得本次完整技术认证';r['evidenceStatus']='UNKNOWN'
   observed.append(dict(routeId=r['id'],diagnosticPurposePassed=selected,rawRun=run,evidence=e,rawInputCaseId=raw['id']))
  g=d['generationContract'];g['generation']['humanReviewRevision']['controlProgramsSha256']=__import__('pcg.prototype.factory.core.quality',fromlist=['digest']).digest([c['control_plan']for c in cs])
  core.write(folder/'module.mapnote.json',d);core.write(folder/'cases.json',dict(cases=cs));core.contract(folder/'module.mapnote.json',refresh=True)
  row.update(contentVersion=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'],canonicalDiagnostics=observed,status='REVISED_REVIEW_DRAFT_NOT_TECHNICALLY_ADMITTED')
  core.write(folder/'review-status.json',dict(schema='pcg/manual-review-candidate-status/v1',reviewId=row['reviewId'],sourceFeedback='feedback/manual-review/batch-001/human-feedback-001.json',sourceVersion=row['sourceVersion'],contentVersion=row['contentVersion'],diagnostics=observed,calibration='NOT_RUN',holdout='NOT_RUN',humanApprovalOfRevision='UNKNOWN',productionApproval=False))
 core.write(OUT/'feedback.json',receipt)
if __name__=='__main__':finalize()
