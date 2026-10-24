"""Record mixed, already-frozen plains witnesses; compare to each original run."""
import argparse,gzip,hashlib,json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from prototype.factory.core.engine import ENGINE
from prototype.factory.core.quality import module_hash

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def event_key(e):
 # Original projectile damage IDs embed Godot ObjectID, which is process-local.
 # Normalize only that suffix; compare every event, time, HP, shot and geometry.
 e=dict(e)
 if e.get('type')=='damage'and str(e.get('source','')).startswith('player_projectile:'):e['source']='player_projectile:<process-object-id>'
 return e
def run(playlist,out,display,reuse=False):
 out.mkdir(parents=True,exist_ok=True);meta=json.loads(playlist.read_text());cases_path=playlist.parent/'review_cases.json';cases=json.loads(cases_path.read_text())['cases'];clips=[]
 assert len(cases)==len(meta['samples'])
 for i,(case,sample)in enumerate(zip(cases,meta['samples'])):
  assert module_hash(case)==case['module_sha256'];physics=ROOT/sample['source_run'];raw={}
  for batch in json.loads((physics/'batches.json').read_text()):
   if 'holdout'not in batch['stage']:continue
   data=gzip.decompress((physics/batch['gzip_path']).read_bytes());assert hashlib.sha256(data).hexdigest()==batch['raw_output_sha256']
   raw.update({r['id']:r for r in json.loads(data)['results']})
  r=raw[case['id']];f=r['frames'][-1]
  previous=dict(frame=f['frame']+1,position=[f['x'],f['y']],events=dict(jump=r['jumps'],air_jump=r['air_jumps'],anchor_jump=r['anchor_jumps'],wall_jump=r['wall_jumps'],shot=r['shots'],hook_cast=r['grapples'],hook_contact=r['hook_contacts']))
  avi=out/f'sample-{i+1:02}.avi';log=out/f'record-{i+1:02}.log';trace_path=out/f'native-trace-{i+1:02}.json'
  if avi.exists()or log.exists():
   if not reuse or not(avi.exists()and log.exists()):raise ValueError('Keep previous evidence; choose another directory')
  else:
   cmd=[str(ENGINE),'--path',str(ROOT/'prototype/godot'),'--audio-driver','Dummy','--write-movie',str(avi.resolve()),'--fixed-fps','60','res://movie_plains.tscn','--','--cases-json',str(cases_path.resolve()),'--case',str(i),'--trace-json',str(trace_path.resolve())]
   (out/f'command-{i+1:02}.json').write_text(json.dumps(cmd))
   with log.open('w')as fh:subprocess.run(cmd,env=dict(os.environ,DISPLAY=display,LIBGL_ALWAYS_SOFTWARE='1'),stdout=fh,stderr=subprocess.STDOUT,check=True,timeout=180)
  text=log.read_text();assert 'SCRIPT ERROR'not in text and 'ERROR:'not in text and 'were leaked'not in text,text[-2000:]
  result=json.loads(next(l.split(' ',1)[1]for l in text.splitlines()if l.startswith('PLAINS_MOVIE_RESULT ')))
  assert result['module_sha256']==case['module_sha256']and result['candidate_uid']==case['factory_id']and result['case_id']==case['id']
  assert result['safe']and result['hp']==5 and result['stable_frames']>=6
  assert result['frame']==previous['frame']and result['events']==previous['events']and max(abs(a-b)for a,b in zip(result['position'],previous['position']))<.001,(result,previous)
  assert [event_key(e)for e in result['plains']['events']]==[event_key(e)for e in r['plains']['events']]
  native=json.loads(trace_path.read_text());assert native['module_sha256']==case['module_sha256']and native['case_id']==case['id'];assert len(native['frames'])==len(r['frames'])
  keys=('frame','x','y','vx','vy','grounded','axis','requested','shot_charges','shot_cooldown','jumps_used','jump_maximum','energy','hp','traversal_state','real_velocity','normal_velocity','module_clock','moving_platforms','saws','support_id','goal_stable_frames')
  max_position_error=0.
  for nf,hf in zip(native['frames'],r['frames']):
   assert all(nf[k]==hf[k]for k in keys),(i,nf['frame'],[(k,nf[k],hf[k])for k in keys if nf[k]!=hf[k]])
   assert [event_key(e)for e in nf['plains']['events']]==[event_key(e)for e in hf['plains']['events']]
   assert nf['plains']['bells']==hf['plains']['bells']and nf['plains']['enemies']==hf['plains']['enemies']
   max_position_error=max(max_position_error,abs(nf['x']-hf['x']),abs(nf['y']-hf['y']))
  mp4=out/f'sample-{i+1:02}.mp4'
  if not mp4.exists():
   with(out/f'encode-{i+1:02}.log').open('w')as fh:subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdout=fh,stderr=subprocess.STDOUT,check=True)
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]));assert probe['streams'][0]['avg_frame_rate']=='60/1'
  clips.append(dict(sample=case.get('review_alias',f'P{i+1:02}'),file=mp4.name,bytes=mp4.stat().st_size,sha256=sha(mp4),duration=float(probe['format']['duration']),module_sha256=case['module_sha256'],candidate_uid=case['factory_id'],engine_result=result,probe=probe,evidence_binding=dict(physics_run=sample['source_run'],physics_binding_sha256=sha(physics/'source_binding.json')),same_as_bound_physics_witness=True,native_trace=dict(file=trace_path.name,bytes=trace_path.stat().st_size,sha256=sha(trace_path),frames=len(native['frames']),exact_fields=list(keys),max_position_error=max_position_error,cell_events_match_at_every_frame=True)))
  print(json.dumps(dict(sample=clips[-1]['sample'],duration=clips[-1]['duration'],native_matches_physics=True)),flush=True)
 concat=out/'concat.txt';concat.write_text(''.join("file '"+c['file']+"'\n"for c in clips));combined=out/'all-samples.mp4'
 with(out/'concat.log').open('w')as fh:subprocess.run(['ffmpeg','-nostdin','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(combined)],stdout=fh,stderr=subprocess.STDOUT,check=True)
 sources=[ROOT/'prototype/godot'/n for n in('movie_plains.gd','movie_plains.tscn','main_plains.gd','plains_cells.gd','main_v3.gd','dynamic_context.gd','lab_draw_v3.gd','plains_lifecycle.gd')]+[Path(__file__)]
 manifest=dict(schema='pcg/video-review/v1',physics_hz=60,playback_speed=1,engine_sha256=sha(ENGINE),cases_sha256=sha(cases_path),playlist_sha256=sha(playlist),source_files={str(p.relative_to(ROOT)):sha(p)for p in sources},clips=clips,combined=dict(file=combined.name,bytes=combined.stat().st_size,sha256=sha(combined)),human_video_feedback=0,human_playtests=0,approved_offline=0,end_hold_seconds=1,review_scope='Actual normal-speed router replay; each complete attempt followed by one second of frozen completion frame; separate uncut clips concatenated in sample order. Finite automated evidence, no human feel or fun approval.')
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--playlist',required=True);p.add_argument('--out',required=True);p.add_argument('--display',default=':103');p.add_argument('--reuse-existing',action='store_true');a=p.parse_args();run(ROOT/a.playlist,ROOT/a.out,a.display,a.reuse_existing)
