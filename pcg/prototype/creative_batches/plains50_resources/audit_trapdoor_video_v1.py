"""Retain strict comparison failure; encode its native recording for review only."""
import gzip,json,subprocess
from pathlib import Path
from pcg.prototype.workshop.record import KEYS,ROOT,event_key
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import module_hash
REPO=ROOT.parent
out=REPO/'generation/workshop/plains50/resources/trapdoor-i0';source=ROOT/'results/workshop-plains50-resources-production-v1/round-01'
c=json.loads((out/'review_cases.json').read_text())['cases'][0];assert module_hash(c)==c['module_sha256']
batch=next(x for x in json.loads((source/'batches.json').read_text())if x['batch']==c['factory_evidence']['batch'])
packed=source/batch['gzip_path'];assert file_sha(packed)==batch['gzip_sha256']
r=json.loads(gzip.decompress(packed.read_bytes()))['results'][c['factory_evidence']['index']]
trace=out/'trapdoor-commit.trace.json';native=json.loads(trace.read_text());assert len(native['frames'])==len(r['frames'])
differences=[]
for a,b in zip(native['frames'],r['frames']):
 for k in KEYS:
  if a[k]!=b[k]:differences.append(dict(frame=a['frame'],field=k,native=a[k],physical=b[k]))
 for k in ['bells','enemies']:
  if a['plains'][k]!=b['plains'][k]:differences.append(dict(frame=a['frame'],field='plains.'+k,native=a['plains'][k],physical=b['plains'][k]))
 if [event_key(e)for e in a['plains']['events']]!=[event_key(e)for e in b['plains']['events']]:differences.append(dict(frame=a['frame'],field='plains.events'))
 if a['workshop']!=b['workshop']:differences.append(dict(frame=a['frame'],field='workshop'))
assert differences,'This audit is specifically a strict failure; use original recorder when exact.'
diff=out/'strict-differences-v1.json';diff.write_text(json.dumps(dict(strict_comparison='failed',review_only=True,differences=differences,total_differences=len(differences),no_comparator_relaxation=True),indent=2))
avi=out/'trapdoor-commit.avi';mp4=out/'trapdoor-commit.mp4'
subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],check=True,capture_output=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]));assert probe['streams'][0]['avg_frame_rate']=='60/1'
clip=dict(id=c['review_alias'],family=c['family'],file=mp4.name,sha256=file_sha(mp4),bytes=mp4.stat().st_size,duration=float(probe['format']['duration']),frames_exact=0,native_frames=len(r['frames']),strict_comparison='failed',review_only=True,strict_differences=diff.name,strict_differences_sha256=file_sha(diff),different_fields=sorted({x['field']for x in differences}),difference_count=len(differences),case_sha256=c['module_sha256'],physics_run=str(source.relative_to(REPO)),physics_binding_sha256=file_sha(source/'source_binding.json'),native_trace_sha256=file_sha(trace),speed=1,human_fun='unreviewed')
(out/'manifest.json').write_text(json.dumps(dict(schema='pcg/video-review/v1',clips=[clip],strict_comparison='failed',review_only=True,no_comparator_relaxation=True,source_audit=str(Path(__file__).relative_to(REPO)),source_sha256=file_sha(Path(__file__)),human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(clip),flush=True)
