"""Index four strict native films and retain the failed end-hold attempt."""
from pathlib import Path
import hashlib,json,gzip,shutil
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rel(p):return str(p.relative_to(ROOT.parent))
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-enemy-world-videos-v2';clips=[]
 labels={'clear':('E01','清敌后露出射铃线','main20'),'displace':('E02','击退活敌，让出真实安全落位','main20'),'attack':('E03','借敌人真实发射开门，离开锁定弹道','extra_independent21'),'lure':('E04','诱冲占区并赶在再次追击前过门','extra_not_counted_independent')}
 for key,(review_id,title,role)in labels.items():
  folder=out/key;m=json.loads((folder/'manifest.json').read_text());c=m['clips'][0];movie=folder/c['file']
  assert sha(movie)==c['sha256']
  for p,h in m['recording_source_files'].items():assert sha(ROOT.parent/p)==h,(p,'source changed')
  if key=='attack':
   trace=json.loads((folder/'enemy-attack-relay.trace.json').read_text())['frames'];run=ROOT.parent/c['physics_run'];case=json.loads((folder/'review_cases.json').read_text())['cases'][0];ev=case['factory_evidence'];b=next(x for x in json.loads((run/'batches.json').read_text())if x['batch']==ev['batch']);physics=json.loads(gzip.decompress((run/b['gzip_path']).read_bytes()))['results'][ev['index']]['frames']
   assert all(a['enemy_world']==b['enemy_world']for a,b in zip(trace,physics));c['native_projectile_and_gate_observer_exact']=True
  c.update(review_id=review_id,title=title,selection_role=role,path=rel(movie),manifest=rel(folder/'manifest.json'),human_video_observation='unreviewed',end_hold='1 sec, no cuts; custom-scene v2 disables world descendants only after final witness frame')
  clips.append(c)
 files=[HERE/'main_v2.gd',HERE/'main_v2.tscn',HERE/'main_v1.gd',HERE/'world_cells_binding_v1.gd',HERE/'attack_relay_v1.gd',HERE/'guard_charger_v1.tres',HERE.parent/'occupancy/binding_v1.gd',HERE.parent/'occupancy/occupancy_latch_v1.gd',HERE/'record_v3.py',HERE/'record_v4.py',Path(__file__),ROOT/'prototype/workshop/record.py',ROOT/'prototype/workshop/main.gd',ROOT/'prototype/workshop/mechanics.gd']
 freeze=out/'source_snapshot'
 for p in files:
  dest=freeze/p.relative_to(ROOT.parent);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
 (out/'source-manifest.json').write_text(json.dumps({rel(p):sha(p)for p in files},indent=2)+'\n')
 failed=ROOT/'results/workshop-creative-enemy-world-videos-v1/lure';failure=dict(path=rel(failed),stage='native recorder log rejection after real final witness frame',reason='EnemyActor explicit PAUSABLE kept processing during display end-hold after parent world disabled; native body_test_motion body->get_space null',retained_avi=rel(failed/'enemy-lure-sensor.avi'),retained_avi_sha256=sha(failed/'enemy-lure-sensor.avi'),log=rel(failed/'enemy-lure-sensor.record.log'),log_sha256=sha(failed/'enemy-lure-sensor.record.log'),resolution='new isolated main_v2 disables all world descendants only after final recorded frame; full strict frame/cell/resource replay passes; final video uses v2',old_headless_consumer_note='old comparison checked all motion frames but omitted log ERROR scan; action frame equality remains, complete lifecycle approval withdrawn')
 playlist=dict(schema='pcg/video-review/v1',producer_task='/root/enemy_world_creator',clips=clips,frames_exact=sum(x['frames_exact']for x in clips),playback_speed=1,frame_rate='60/1',end_hold_seconds=1,human_playtest='unreviewed',human_fun='unreviewed',production_admitted=False,failed_attempts=[failure],earlier_ordinary_films='videos-v1 clear/displace retained; v2 re-recorded after shared recorder --scene code stabilized; bytes identical',frame_inspection='each clip decoded successfully; clear/displace frame-check in videos-v1, attack/lure frame-check in videos-v2',source_manifest=rel(out/'source-manifest.json'))
 (out/'playlist.json').write_text(json.dumps(playlist,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(dict(path=rel(out/'playlist.json'),clips=len(clips),total_verified_frames=playlist['frames_exact'],files=[x['path']for x in clips]),ensure_ascii=False))
