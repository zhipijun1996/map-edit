"""Full retained per-clip comparison reports, unchanged exact recording rule."""
import json,gzip,hashlib,subprocess
from pathlib import Path
from pcg.prototype.workshop.record import KEYS
from pcg.tools.record_plains import event_key
from pcg.prototype.factory.core.engine import file_sha
OWN=Path(__file__);REPO=OWN.resolve().parents[4];BASE=REPO/'pcg/results/workshop-creative-jump-wall-native-v2';OUT=REPO/'pcg/creative-production/jump_wall/native-comparison-v1.json'
if OUT.exists():raise ValueError('immutable_comparison_exists')
playlist=json.loads((BASE/'manifest.json').read_text());reports=[]
for item in playlist['clips']:
 assert item['status']=='exact_native_pass'
 folder=REPO/item['manifest'];folder=folder.parent
 clip=item['clips'][0];case=json.loads((folder/'review_cases.json').read_text())['cases'][0];trace=folder/(item['family']+'.trace.json');native=json.loads(trace.read_text());source=REPO/clip['physics_run'];ev=case['factory_evidence'];b=next(b for b in json.loads((source/'batches.json').read_text())if b['batch']==ev['batch']);packed=source/b['gzip_path'];raw=gzip.decompress(packed.read_bytes());assert file_sha(packed)==b['gzip_sha256']and hashlib.sha256(raw).hexdigest()==b['raw_output_sha256'];r=json.loads(raw)['results'][ev['index']]
 assert r['id']==case['id']==native['case_id']and native['module_sha256']==case['module_sha256'];assert len(native['frames'])==len(r['frames'])
 diffs=[]
 for nf,hf in zip(native['frames'],r['frames']):
  for k in KEYS:
   if nf[k]!=hf[k]:diffs.append(dict(frame=hf['frame'],field=k,native=nf[k],physics=hf[k]))
  cells=[('plains.events',[event_key(e)for e in nf['plains']['events']],[event_key(e)for e in hf['plains']['events']]),('plains.bells',nf['plains']['bells'],hf['plains']['bells']),('plains.enemies',nf['plains']['enemies'],hf['plains']['enemies']),('workshop',nf['workshop'],hf['workshop'])]
  for k,a,bv in cells:
   if a!=bv:diffs.append(dict(frame=hf['frame'],field=k,native=a,physics=bv))
 mp4=folder/clip['file'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]));video=probe['streams'][0]
 assert file_sha(mp4)==clip['sha256']and file_sha(trace)==clip['native_trace_sha256']and video['avg_frame_rate']=='60/1'and video['pix_fmt']=='yuv420p'
 report=dict(id=case['id'],family=item['family'],mp4_path=str(mp4.relative_to(REPO)),mp4_sha256=file_sha(mp4),bytes=mp4.stat().st_size,duration=float(probe['format']['duration']),video_probe=dict(codec=video['codec_name'],frame_rate=video['avg_frame_rate'],width=video['width'],height=video['height'],pixel_format=video['pix_fmt'],encoded_frames=video['nb_frames']),native_trace_path=str(trace.relative_to(REPO)),native_trace_sha256=file_sha(trace),physics_run=clip['physics_run'],physics_binding_sha256=file_sha(source/'source_binding.json'),source_case_sha256=case['module_sha256'],frames_compared=len(r['frames']),exact_fields=list(KEYS),frame_cell_fields=['plains.events','plains.bells','plains.enemies','workshop'],differences=diffs,comparison_pass=not diffs,threshold_unchanged=True,normalization='Original event_key only normalizes process-local player_projectile ObjectID suffix; no additional normalization.',end_hold_seconds=1,speed=1)
 path=folder/'exact-comparison-v1.json';assert not path.exists();path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');reports.append(report);assert not diffs
summary=dict(schema='pcg/native-comparison-playlist/v1',clips=reports,comparison_threshold_unchanged=True,all_exact=all(r['comparison_pass']for r in reports),total_physics_frames=sum(r['frames_compared']for r in reports),total_mp4_bytes=sum(r['bytes']for r in reports),normal_playback_speed=1,source_files=playlist['source_files'],prior_native_version='pcg/results/workshop-creative-jump-wall-native-v1/manifest.json',human_fun='unreviewed',manual_play='not_done',production_admitted=False)
OUT.write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n');print(json.dumps(dict(file=str(OUT.relative_to(REPO)),clips=len(reports),all_exact=summary['all_exact'],frames=summary['total_physics_frames'],bytes=summary['total_mp4_bytes']),ensure_ascii=False),flush=True)
