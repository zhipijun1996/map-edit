"""Fresh-process original-library retrieval and eight-version publication index."""
import json,hashlib,shutil,copy
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.workshop.library import WorkshopLibrary
from .rules_v2 import RECIPES
REPO=ROOT.parent
OUT=REPO/'generation/workshop/plains50-enemy-v1'
NAMES={'attack-relay':'引敌开门','clear-sightline':'清除吸弹射界','live-enemy-sensor':'保留活体供电','displace-landing':'击退腾出落位'}
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def binding(p):return dict(path=str(p.relative_to(REPO)),sha256=sha(p))
if __name__=='__main__':
 if OUT.exists():raise ValueError('immutable_publication_exists')
 rows=[];retrieval=[];total=0;pilots=0;held_total=0;held_ok=0;cal_total=0;cal_ok=0;counter_total=0
 for recipe in RECIPES:
  parent=ROOT/'results'/('workshop-plains50-enemy-r2-'+recipe);run=parent/'round-00';summary=read(parent/'summary.json');assert summary['new_candidates']==2
  total+=summary['physics_cases'];held=read(run/'evaluations.json');cal=read(run/'calibration-evaluations.json');held_total+=sum(len(x['rows'])for x in held);held_ok+=sum(y['purpose']['ok']for x in held for y in x['rows']);cal_total+=sum(len(x['rows'])for x in cal);cal_ok+=sum(y['purpose']['ok']for x in cal for y in x['rows']);counter_total+=len(read(run/'counterexamples.json'));pilot=read(ROOT/'results'/('workshop-plains50-enemy-probe-v1-'+recipe)/'summary.json');pilots+=len(pilot)
  assert summary['physics_cases']+len(pilot)<=400
  specs=read(run/'challenge-specifications.json');expected=set(summary['ledger'][0]['versions'])
  for interface,spec in enumerate(specs):
   hits=WorkshopLibrary(ROOT/'map_directed/library').find_single_exact(spec);chosen=[h for h in hits if h['record']['contentVersion']in expected];assert len(chosen)==1
   h=chosen[0];record=h['record'];folder=(REPO/h['path']).parent;doc=folder/'module.mapnote.json';d=read(doc)
   assert record['production_admitted']is False and record['technical_status']=='passed_scoped'
   assert set(h['case']['capabilities'])=={'move','jump','shot_recoil'}
   media=ROOT/'results/workshop-plains50-enemy-media-v1'/recipe;movie=read(media/'manifest.json');clip=movie['clips'][0]
   assert clip['frames_exact']>0 and clip['cell_events_exact']and clip['reward_and_carrier_state_exact']
   rows.append(dict(id=f'E{len(rows)+1:02}',title=NAMES[recipe]+(' · 近接口'if interface==0 else' · 远/低接口'),recipe=recipe,interface=interface,contentVersion=record['contentVersion'],port_count=2,relations='entry→exit only; reverse/state/seams UNKNOWN',specification=spec,document=binding(doc),record=binding(folder/'record.json'),case_id=h['case']['id'],case_sha256=record['case_sha256'],source_run=str(run.relative_to(REPO)),main_scene='pcg/prototype/creative_batches/enemy_world/main_v2.tscn',video_representative=interface==0,video=clip if interface==0 else None,group_video_not_a_recording_for_this_exact_adapter=interface!=0,human_fun='UNKNOWN',production_admitted=False))
   wrong=copy.deepcopy(spec);wrong['objective']['spatial_demand']['exit_x']+=19;assert not WorkshopLibrary(ROOT/'map_directed/library').find_single_exact(wrong)
   retrieval.append(dict(specification=spec['id'],contentVersion=record['contentVersion'],generator_called=False,physical_cases=0,from_existing_candidate_store=True,wrong_exit_demand_rejected=True))
 OUT.mkdir(parents=True);(OUT/'videos').mkdir();(OUT/'modules').mkdir()
 for recipe in RECIPES:
  run=ROOT/'results'/('workshop-plains50-enemy-r2-'+recipe)/'round-00';media=ROOT/'results/workshop-plains50-enemy-media-v1'/recipe;clip=read(media/'manifest.json')['clips'][0]
  shutil.copy2(media/clip['file'],OUT/'videos'/clip['file'])
  for p in (run/'modules').glob('*'):
   if p.suffix in ['.json','.svg']and p.name!='manifest.json':shutil.copy2(p,OUT/'modules'/p.name)
 for row in rows:
  if row['video']:
   file=OUT/'videos'/row['video']['file'];assert sha(file)==row['video']['sha256'];row['video']['public_path']=str(file.relative_to(REPO))
 manifest=dict(schema='pcg/plains50-enemy-publication/v1',versions=8,existing_relationships=4,new_action_families_claimed=0,full_production_physics_cases=total,pilot_physics_cases=pilots,total_real_physics_cases=total+pilots,strict_video_representatives=4,held_purpose_passes=held_ok,held_trials=held_total,calibration_purpose_passes=cal_ok,calibration_trials=cal_total,cheap_counterexamples=counter_total,shared_physics_or_harness_modified=False,library='pcg/map_directed/library',modules=rows,persistent_retrieval=retrieval,new_physics_in_retrieval=0,original_quality='regular unchanged',human_fun='UNKNOWN',production_admitted=False)
 (OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 (OUT/'retrieval.json').write_text(json.dumps(retrieval,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps({k:v for k,v in manifest.items()if k not in ['modules','persistent_retrieval']},ensure_ascii=False))
