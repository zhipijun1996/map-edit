"""Read completed original library versions and replay metadata; no generation."""
import argparse,json
from pathlib import Path
from pcg.prototype.workshop.library import WorkshopLibrary
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent
RUNS=['workshop-plains50-terrain-adapt-v1/round-00','workshop-plains50-terrain-adapt-v1/round-01','workshop-plains50-terrain-relay-v2/round-00','workshop-plains50-terrain-column-v3/round-00']
TITLES={'slot-low-approach':'窄道：较高接收岸','slot-wide-exit':'窄道：宽出口岸','brake-short-pocket':'过檐刹入：短侧袋','brake-deep-pocket':'过檐刹入：深侧袋','reload-level-relay':'落地补枪：水平接力','reload-rising-relay':'落地补枪：抬升接力','column-low-exit':'柱底救回：低侧岸','column-wide-turn':'柱底救回：宽转折'}

def inventory():
 modules=[];retrieved=[];lib=WorkshopLibrary(ROOT/'module_library/store');video_files=list((REPO/'generation/workshop/plains50-terrain-v1/videos').glob('*/manifest.json'))
 for run in RUNS:
  source=ROOT/'results'/run;cs=json.loads((source/'review_cases.json').read_text())['cases'];manifest=json.loads((source/'modules/manifest.json').read_text());cal=json.loads((source/'calibration-evaluations.json').read_text());held=json.loads((source/'evaluations.json').read_text())
  for item in manifest['modules']:
   version=item['contentVersion'];dest=ROOT/'module_library/store/candidates'/version.removeprefix('sha256:');record=json.loads((dest/'record.json').read_text());case=json.loads((dest/'case.json').read_text());spec=case['map_specification'];matches=lib.find_single_exact(spec)
   assert any(m['record']['contentVersion']==version for m in matches),'missing persistent exact retrieval '+version
   retrieved.append(dict(specification=spec['id'],version=version,match_versions=[m['record']['contentVersion']for m in matches],generator_called=False,physics_cases=0))
   witness=next(c for c in cs if c['factory_id']==item['id'].removeprefix('generated-'));base_id=witness['review_alias'];key=next(k for k in TITLES if '-'+k+'-control-'in base_id)
   videos=[]
   for vp in video_files:
    for clip in json.loads(vp.read_text())['clips']:
     if clip['id']!=base_id:continue
     movie=vp.parent/clip['file'];assert file_sha(movie)==clip['sha256'];videos.append(dict(path=str(movie.relative_to(REPO)),sha256=clip['sha256'],manifest=str(vp.relative_to(REPO)),duration=clip['duration'],frames_exact=clip['frames_exact'],native_trace_sha256=clip['native_trace_sha256'],strict_comparison='passed'))
   def rates(entries):
    row=next(e for e in entries if e['case']['id']==base_id);return dict(status=row['quality_gate']['status'],rates={k:v['rate']for k,v in row['stats'].items()})
   modules.append(dict(id=item['id'],title=TITLES[key],contentVersion=version,family=item['family'],recipe=spec['objective']['recipe'],parameters=spec['objective']['parameters'],portCount=2,relations=[dict(from_port='entry',to_port='exit',status='scoped_witness')],return_status='UNKNOWN',seams='UNKNOWN',document=str((dest/'module.mapnote.json').relative_to(REPO)),document_sha256=record['document_sha256'],svg=str((source/'modules'/(item['id']+'.svg')).relative_to(REPO)),case_file=str((dest/'case.json').relative_to(REPO)),source_run=str(source.relative_to(REPO)),source_binding_sha256=file_sha(source/'source_binding.json'),specification=spec,calibration=rates(cal),holdout=rates(held),videos=videos,technical_status=record['technical_status'],human_fun='UNKNOWN',human_playtest='UNKNOWN',production_admitted=False))
 assert len(modules)==8
 return dict(schema='pcg/plains50-owner-delivery/v1',owner='/root/plains50_terrain',modules=modules,new_versions=8,recipe_count=4,new_family_claim='not established:2 existing adapters,1 existing crossed-gap ground-resource composition,1 downward-clearance rescue subrelationship pending independent grouping',formal_production_physics_cases=832,design_probe_cases=40,actual_total_physics_cases=872,capabilities=['move','jump','shot_recoil'],all_failures_retained=True,source_directories=['pcg/prototype/creative_batches/plains50_terrain'],raw_runs=['pcg/results/'+r for r in ['workshop-plains50-terrain-adapt-v1','workshop-plains50-terrain-relay-probe-v1','workshop-plains50-terrain-relay-probe-v2','workshop-plains50-terrain-column-probe-v3','workshop-plains50-terrain-relay-v2','workshop-plains50-terrain-column-v3']],fresh_process_retrieval=retrieved,retrieval_physics_cases=0,human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False)

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path);a=p.parse_args();r=inventory()
 if a.out:
  if a.out.exists():raise ValueError('immutable_delivery_receipt_exists')
  a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
 else:print(json.dumps(r,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
