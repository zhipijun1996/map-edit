"""Publish exact admitted versions; metadata view on original persistent library."""
import json,shutil
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent
RUNS=['workshop-plains50-new-brake-production-v1/round-00','workshop-plains50-new-resource-production-v1/round-00','workshop-plains50-new-resource-production-v1/round-01','workshop-plains50-new-adverse-production-v2/round-00','workshop-plains50-new-sequence-production-v1/round-00']
NAMES={'brake-gate-catch':'开侧门的一枪也是刹车','adverse-refund-reversal':'补给把你推离目标','refill-short-gate':'把回充枪投给高处短门','prepared-air-sequence':'先备第一铃，再跃短门'}
VIDEO_DIRS={'brake-gate-catch':'brake-gate','adverse-refund-reversal':'adverse-refund','refill-short-gate':'refill-gate','prepared-air-sequence':'prepared-sequence'}

def publish():
 out=REPO/'generation/workshop/plains50-new-relations';modules=out/'modules';modules.mkdir(parents=True,exist_ok=True);items=[]
 for run in RUNS:
  r=ROOT/'results'/run;entries=json.loads((r/'modules/manifest.json').read_text())['modules'];cases=json.loads((r/'review_cases.json').read_text())['cases'];evals=json.loads((r/'evaluations.json').read_text())
  for row in entries:
   src=r/'modules'/row['file'];doc=json.loads(src.read_text());v=row['contentVersion'];lp=ROOT/'module_library/store/candidates'/v.removeprefix('sha256:');record=json.loads((lp/'record.json').read_text());assert file_sha(src)==record['document_sha256'];assert record['technical_status']=='passed_scoped'
   case=next(c for c in cases if 'generated-'+c['factory_id']==doc['id']);spec=case['map_specification'];q=next(e for e in evals if e['case']['id']==case['review_alias']);assert q['quality_gate']['status']=='awaiting_human_review'
   target=modules/src.name
   if target.exists():assert target.read_bytes()==src.read_bytes()
   else:shutil.copy2(src,target)
   svg=r/'modules'/(doc['id']+'.svg');dest=modules/svg.name
   if dest.exists():assert dest.read_bytes()==svg.read_bytes()
   else:shutil.copy2(svg,dest)
   family=row['family'];vf=out/'videos'/VIDEO_DIRS[family]/'manifest.json';videos=json.loads(vf.read_text())['clips']if vf.exists()else[]
   items.append(dict(id=f'PN{len(items)+1:02d}',title=NAMES[family],family=family,contentVersion=v,portCount=len(doc['generationContract']['ports']),document=str(target.relative_to(REPO)),document_sha256=file_sha(target),svg=str(dest.relative_to(REPO)),svg_sha256=file_sha(dest),source_run=str(r.relative_to(REPO)),record=str((lp/'record.json').relative_to(REPO)),specification=spec,case_id=case['id'],case_sha256=case['module_sha256'],holdout_rates={k:x['rate']for k,x in q['stats'].items()},video_manifest=str(vf.relative_to(REPO))if vf.exists()else'PENDING',representative_video_covers_this_exact_version=bool(videos and videos[0]['case_sha256']==case['module_sha256']),capabilities=['move','jump','shot_recoil'],human_fun='unreviewed',human_playtest='UNKNOWN',production_admitted=False))
 manifest=dict(schema='pcg/owner-content-delivery/v1',owner='/root/plains50_new_relations',items=items,module_versions=len(items),recipe_count=len(set(i['family']for i in items)),new_family_claim=False,library='pcg/module_library/store',source_design_cards='pcg/prototype/creative_batches/plains50_new_relations/design-cards-v2.json',feedback='pcg/feedback/workshop/plains50-new-relations-design-gaps-v1.json',production_admitted=False)
 target=out/'manifest.json'
 if target.exists():raise ValueError('immutable_owner_publication_exists')
 target.write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');print(target)
if __name__=='__main__':publish()
