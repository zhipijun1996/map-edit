"""Index this owner's real admitted candidates, existing evidence and videos."""
import json
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent
HERE=Path(__file__).parent
GROUPS=[('P50-R01','sightline-backtrack','先去东侧看清，开门后向西','workshop-plains50-resources-sightline-production-v2/round-00','sightline-i0'),('P50-R02','trapdoor-commit','撤掉脚下桥，承诺进入下层','workshop-plains50-resources-production-v1/round-01','trapdoor-i0'),('P50-R03','ordered-target-transaction','先留进度，再把第二枪送对铃','workshop-plains50-resources-production-v1/round-02','order-i0'),('P50-R04','low-ray-recoil-return','低射界开锁后回升落位','workshop-plains50-resources-lowray-production-v2/round-00','lowray-overview-i0')]
RAW_RUNS=['workshop-plains50-resources-probe-v1','workshop-plains50-resources-production-v1','workshop-plains50-resources-lowray-probe-v1','workshop-plains50-resources-lowray-production-v1','workshop-plains50-D03-resource-probe-v1','workshop-plains50-resources-sightline-production-v2','workshop-plains50-resources-lowray-probe-v2','workshop-plains50-resources-lowray-production-v2','workshop-plains50-resources-reuse-v1']

def binding(p):return dict(path=str(p.relative_to(REPO)),sha256=file_sha(p))
def main():
 out=REPO/'generation/workshop/plains50/resources';target=out/'manifest.json'
 if target.exists():raise ValueError('immutable_delivery_index')
 rows=[]
 for group,recipe,title,run,video_dir in GROUPS:
  root=ROOT/'results'/run;manifest=json.loads((root/'modules/manifest.json').read_text());entries=json.loads((root/'evaluations.json').read_text());cal=json.loads((root/'calibration-evaluations.json').read_text())
  video_manifest=out/video_dir/'manifest.json';media=json.loads(video_manifest.read_text());clip=media['clips'][0]
  for item in manifest['modules']:
   version=item['contentVersion'];folder=ROOT/'module_library/store/candidates'/version.removeprefix('sha256:');record=json.loads((folder/'record.json').read_text());case=json.loads((folder/'case.json').read_text());doc=json.loads((folder/'module.mapnote.json').read_text());interface=case['interface'];entry=next(e for e in entries if e['case']['id']==case['review_alias']);ce=next(e for e in cal if e['case']['id']==case['review_alias'])
   assert record['technical_status']=='passed_scoped' and entry['quality_gate']['status']=='awaiting_human_review'
   assert file_sha(folder/'module.mapnote.json')==record['document_sha256']
   row=dict(id=group+('A'if interface==0 else'B'),title=title+f' · 接口{interface+1}',family=recipe,interface=interface,contentVersion=version,kind=doc['generationContract']['kind'],portCount=len(doc['generationContract']['ports']),tested_capabilities=case['capabilities'],specification=case['map_specification'],document=binding(folder/'module.mapnote.json'),source_case=binding(folder/'case.json'),library_record=binding(folder/'record.json'),source_run=str(root.relative_to(REPO)),case_id=case['id'],review_alias=case['review_alias'],calibration=ce['stats'],independent_holdout=entry['stats'],technical_status=record['technical_status'],technical_scope=record['technical_scope'],new_family_claim=False if recipe!='low-ray-recoil-return'else'pending_independent_ai_curation',assembly='UNKNOWN; new placement/continuous Map evidence required',human_video_observation='unreviewed',human_playtest='UNKNOWN',production_admitted=False)
   if interface==0:
    movie=out/video_dir/clip['file'];assert file_sha(movie)==clip['sha256'];row['video']=dict(**binding(movie),duration=clip['duration'],strict_comparison=clip.get('strict_comparison','passed'),review_only=clip.get('review_only',False),manifest=binding(video_manifest),frames_exact=clip['frames_exact'])
   else:row['video']='UNKNOWN; first-interface clip only illustrates shared relation, does not prove this exact version'
   if recipe=='low-ray-recoil-return':row['play_scene']='pcg/prototype/creative_batches/plains50_resources/main_lowray_overview_v1.tscn'
   elif recipe=='ordered-target-transaction':row['play_scene']='pcg/prototype/creative_batches/creative_catalog/main-sequence-portable-v1.tscn'
   else:row['play_scene']='pcg/prototype/workshop/main.tscn'
   rows.append(row)
 physics=0;run_receipts=[]
 for name in RAW_RUNS:
  p=ROOT/'results'/name;count=0
  for b in p.rglob('batches.json'):count+=sum(r['cases']for r in json.loads(b.read_text()))
  physics+=count;run_receipts.append(dict(path=str(p.relative_to(REPO)),physics_cases=count))
 assert len(rows)==8 and physics==1190
 result=dict(schema='pcg/plains50-resource-delivery/v1',owner='/root/plains50_resources',candidate_versions=8,recipe_relationships=4,new_action_families='not_self_admitted; three adapted existing families, low-ray relation awaits independent grouping',capabilities=['move','jump','shot_recoil'],physical_godot_cases=physics,physics_budget_by_recipe=dict(sightline_backtrack=382,trapdoor_commit=218,ordered_target_transaction=234,low_ray_recoil_return=352,D03_mechanism_only=4),raw_runs=run_receipts,design_cards=binding(HERE/'design-cards-v1.json'),D03_gap=binding(ROOT/'feedback/workshop/plains50-resources-D03-gap-v1.json'),persistent_retrieval=binding(ROOT/'results/workshop-plains50-resources-reuse-v1/receipt.json'),rows=rows,video_summary=dict(representative_clips=4,exact_clips=3,review_only_clips=1,trapdoor_strict_differences='34 support_id differences, no comparator relaxation',lowray_old_camera='Original camera clip retained in lowray-i0; new overview clip includes real receiver and is separately strict-compared.'),unknowns=['General reverse relations, post-failure retry and continuous recovery remain UNKNOWN unless separately stated in original contract.','PR-D03 complete persistent scarce-enemy two-route generator is missing.','World assembly/Map validation and human fun/production approval are not implied.'],production_admitted=False)
 target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(target)
if __name__=='__main__':main()
