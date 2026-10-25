"""Index three exact films and one honest failed-strict review film."""
import gzip,json,subprocess
from pathlib import Path
from pcg.prototype.workshop.record import KEYS
from pcg.tools.record_plains import event_key
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
HERE=Path(__file__).parent;REPO=ROOT.parent
out=ROOT/'results/workshop-creative-resource-routes-native-v1'
index=out/'manifest-v1.json'
if index.exists():raise ValueError('immutable media index')
clips=[]
for folder in ['sightline','ordered-target','moving-ray']:
 base=out/folder;m=json.loads((base/'manifest.json').read_text());c=m['clips'][0]
 c.update(strict_comparison='passed',raw_directory=str(base.relative_to(REPO)),file=str((base/c['file']).relative_to(REPO)),original_movie_manifest=str((base/'manifest.json').relative_to(REPO)))
 clips.append(c)
base=out/'trapdoor';case=json.loads((base/'review_cases.json').read_text())['cases'][0]
rd=ROOT/'results/workshop-creative-resource-routes-v5/round-02';ev=case['factory_evidence'];b=next(x for x in json.loads((rd/'batches.json').read_text())if x['batch']==ev['batch'])
r=json.loads(gzip.decompress((rd/b['gzip_path']).read_bytes()))['results'][ev['index']]
trace=base/'trapdoor-commit.trace.json';native=json.loads(trace.read_text());assert len(native['frames'])==len(r['frames'])and native['module_sha256']==case['module_sha256']
diffs=[]
for a,z in zip(native['frames'],r['frames']):
 for k in KEYS:
  if a[k]!=z[k]:diffs.append(dict(frame=a['frame'],field=k,native=a[k],batch=z[k]))
 for k in ['bells','enemies']:
  if a['plains'][k]!=z['plains'][k]:diffs.append(dict(frame=a['frame'],field='plains.'+k,native=a['plains'][k],batch=z['plains'][k]))
 if [event_key(e)for e in a['plains']['events']]!=[event_key(e)for e in z['plains']['events']]:diffs.append(dict(frame=a['frame'],field='plains.events',native=a['plains']['events'],batch=z['plains']['events']))
 if a['workshop']!=z['workshop']:diffs.append(dict(frame=a['frame'],field='workshop',native=a['workshop'],batch=z['workshop']))
assert diffs and all(x['field']=='support_id'for x in diffs)
log=(base/'trapdoor-commit.record.log').read_text();completion=json.loads(next(line.split('WORKSHOP_MOVIE_RESULT ',1)[1]for line in log.splitlines()if 'WORKSHOP_MOVIE_RESULT 'in line))
assert completion['safe']and completion['hp']==5 and completion['stable_frames']>=6
assert not any(x in log for x in ['ERROR:','SCRIPT ERROR','were leaked'])
avi=base/'trapdoor-commit.avi';mp4=base/'trapdoor-commit.review-only.mp4'
with(base/'review-only-encode.log').open('w')as f:subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdout=f,stderr=subprocess.STDOUT,check=True)
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]));assert probe['streams'][0]['avg_frame_rate']=='60/1'
(base/'strict-differences-v1.json').write_text(json.dumps(diffs,indent=2))
clips.append(dict(id=case['review_alias'],family=case['family'],file=str(mp4.relative_to(REPO)),sha256=file_sha(mp4),bytes=mp4.stat().st_size,duration=float(probe['format']['duration']),native_frames=len(native['frames']),strict_comparison='failed',differences_file=str((base/'strict-differences-v1.json').relative_to(REPO)),difference_count=len(diffs),difference_fields=sorted({x['field']for x in diffs}),all_other_original_fields_exact=True,case_sha256=case['module_sha256'],physics_run=str(rd.relative_to(REPO)),native_trace_sha256=file_sha(trace),raw_directory=str(base.relative_to(REPO)),native_completion=completion,review_only=True,speed=1,human_fun='unreviewed'))
(index).write_text(json.dumps(dict(schema='pcg/resource-routes-native-review/v1',clips=clips,exact_video_count=3,failed_strict_video_count=1,fps='60/1',speed=1,end_hold_seconds=1,end_hold='whole world frozen, retained',all_intra_clip_frames_retained=True,comparison_policy='original record.KEYS plus original event_key plus exact bells/enemies/workshop; no relaxed fields',recording_sources={str(p.relative_to(REPO)):file_sha(p)for p in [Path(__file__),HERE/'main-sequence-v1.gd',HERE/'main-sequence-v1.tscn',REPO/'pcg/prototype/workshop/record.py']},human_playtest=False,production_admitted=False),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(dict(manifest=str(index.relative_to(REPO)),exact=3,failed_strict=1,differences=len(diffs))))
