"""Second and final geometry revision for the first human feedback batch."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pathlib import Path
import copy,shutil
from pcg.migration import core,godot_package
ROOT=core.REPO;BEFORE=ROOT/'pcg/manual_review/batch-001/revision-001';OUT=BEFORE.with_name('revision-002')
def prepare():
 if OUT.exists():raise ValueError('immutable_revision_exists')
 receipt=core.read(BEFORE/'feedback.json');receipt['revision']='revision-002';receipt['previousRevision']='revision-001'
 for row in receipt['rows']:
  src=ROOT/row['candidate'];folder=OUT/row['moduleId'];d=core.read(src/'module.mapnote.json');cs=core.read(src/'cases.json')['cases'];g=d['generationContract']
  if row['reviewId']=='01':
   o=next(o for o in d['objects']if o.get('sourceId')=='review-center-diver');o['y']=464
  if row['reviewId']=='03':
   o=next(o for o in d['objects']if o.get('sourceId')=='review-gap-diver');o['x']=-78;o['y']=384;o['mechanics']['initialIdleCooldown']=0.6
  for c in cs:c.update(copy.deepcopy(godot_package.content_from_objects(d)))
  if row['reviewId']=='02':
   c=cs[0];p=c['control_plan'];j=next(j for j,v in enumerate(p)if v.get('target_x')==1136)
   p[j]['target_x']=1108
   for v in p[j+1:]:
    dyn=v.get('trigger',{}).get('dynamic',{})
    if dyn.get('kind')=='actor_x'and dyn.get('value')==1130:dyn['value']=1102;break
   j=next(k for k in range(j,len(p))if p[k]['op']=='wait'and p[k]['trigger'].get('state')=='grounded')+1
   p[j:j]=[dict(op='shoot',trigger=dict(after=0 if n==0 else 22),aim_cell=dict(kind='enemy',id='review-crest-sentry'),direction=[1,0])for n in range(3)]
  g['generation']['humanReviewRevision'].update(id='batch-001/revision-002',previousCandidateVersion=g['contentVersion'])
  core.write(folder/'module.mapnote.json',d);core.write(folder/'cases.json',dict(cases=cs));core.contract(folder/'module.mapnote.json',refresh=True)
  row.update(candidate=core.relative(folder),contentVersion=core.read(folder/'module.mapnote.json')['generationContract']['contentVersion'])
 core.write(OUT/'feedback.json',receipt)
if __name__=='__main__':prepare()
