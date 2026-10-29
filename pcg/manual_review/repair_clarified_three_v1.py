"""Freeze the user's clarified three-item implementation scope; no web edits."""
import argparse,copy,inspect,shutil,subprocess
from pathlib import Path
from pcg.migration import core,physics,godot_package,corners
from pcg.prototype.factory.core.quality import digest
from pcg.manual_review import finalize_first40_v1 as shared
from pcg.manual_review.review029_content_v1 import decode
OUT=core.REPO/'feedback/manual-review/implementation-results/clarified-three-v1'
AUTH=OUT/'authorization';WORK=core.REPO/'pcg/manual_review/implementation/clarified-three-work-v1';FINAL=core.REPO/'pcg/manual_review/implementation/clarified-three-final-v1'
OLD_AUTH=core.REPO/'feedback/manual-review/implementation-results/review-029-v1/authorization'

def prepare():
 assert not (OUT/'prepared.json').exists()
 rows=[r for r in core.read(OLD_AUTH/'handoff.json')['rows']if r['reviewId']in ['171','174','175']]
 core.write(AUTH/'request.json',dict(verbatim=['171就是不让玩家跳，设定是想让玩家左右交替开枪。','174修改不是rock','175需要玩家合适时间起跳'],startingCommit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),scope=['171','174','175'],constraints=dict(noDesignWebEdits=True,no171HeadroomChange=True,require171NoJumpAndAlternatingShots=True,port174Surface='ONE_WAY_PLATFORM',keep175Geometry=True),developmentBudget=dict(maximum171Programs=6,maximum175Programs=6,trialsPerScreenRoute=13,maximumFormalSelectedPerModule=1,selection='first program passing unchanged bounded screen; no holdout selection'),stopping='fixed domains frozen before execution; no formal retries'))
 for r in rows:
  n=r['reviewId'];original=copy.deepcopy(r);old=core.REPO/('pcg/manual_review/implementation/review-029-final-v1'if n!='174'else'pcg/manual_review/implementation/batch-019')/r['moduleId'];d=core.read(old/'module.mapnote.json');cs=core.read(old/'cases.json')['cases'];target=core.read(core.REPO/r['designFile'])
  if n=='174':
   next(p for p in target['ports']if p['id']=='exit')['surface']='ONE_WAY_PLATFORM';target['designVersion']='sha256:'+digest({k:v for k,v in target.items()if k!='designVersion'});r.update(designFile=core.relative(AUTH/'174-authorized-target.json'),designVersion=target['designVersion']);core.write(AUTH/'174-authorized-target.json',target);r['designFileSha256']=core.sha(core.REPO/r['designFile'])
   g=d['generationContract'];p=next(p for p in g['ports']if p['id']=='exit');p['surface']='ONE_WAY_PLATFORM';p['grid'].pop('profile',None)if 'grid'in p else None
   next(p for p in g['ports']if p['id']=='entry')['stagingPosition']=[240,420]
   for c in cs:
    c['id']='clarified-three-174';c['approved_implementation']['designVersion']=r['designVersion'];c['route_spec']['require_bell']=True
   d['generationContract']['generation']['approvedImplementation']['designVersion']=r['designVersion']
  elif n=='171':
   for c in cs:c['generation_rule']['registration_source']='pcg/manual_review/clarified_three_author_v1.py'
  else:
   for c in cs:c['generation_rule']['registration_source']='pcg/manual_review/clarified_three_author_v1.py'
  r['outputDirectory']=core.relative(WORK/r['moduleId']);folder=core.REPO/r['outputDirectory']
  for c in cs:
   c['id']='clarified-three-'+n+'-'+c['route_spec']['id'];c['max_frames']=3000
   for key in ('recorded_frames','module_sha256','factory_evidence','noise'):c.pop(key,None)
   c['generation_rule']['registration_source']='pcg/manual_review/clarified_three_author_v1.py'
  d=godot_package.bind_case_behavior(d,cs);corners.annotate(d);core.write(folder/'module.mapnote.json',d);core.contract(folder/'module.mapnote.json',refresh=True);core.write(folder/'cases.json',dict(cases=cs));core.write(folder/'migration.json',(core.read(old/'migration.json')if (old/'migration.json').exists()else dict(moduleId=r['moduleId'],sourcePath=r['sourceModule']['file'],sourceVersion=r['sourceModule']['contentVersion'],status='prepared_unverified',productionAdmitted=False)));core.write(folder/'parameters.json',dict(content=decode(d),controls=[c['control_plan']for c in cs],original=original));core.write(AUTH/(n+'-original-binding.json'),original)
 core.write(AUTH/'handoff.json',dict(rows=rows));core.write(OUT/'prepared.json',dict(passed=True));print('PREPARED',flush=True)

def rows():return core.read(AUTH/'handoff.json')['rows']
if __name__=='__main__':prepare()
