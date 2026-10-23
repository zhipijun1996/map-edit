"""Native, normal-speed witness videos. No simulation or module edits."""
import argparse,gzip,hashlib,json,os,subprocess
from pathlib import Path
from .core.engine import ROOT,ENGINE
from .core.quality import module_hash

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(out,display,reuse=False,cases_path=None,physics_run=None):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 cases_path=Path(cases_path)if cases_path else ROOT/'results/factory-production-v2/review_cases.json'
 cases=json.loads(cases_path.read_text())['cases']
 if physics_run:
  raw={}
  for batch in json.loads((Path(physics_run)/'batches.json').read_text()):
   if 'holdout'not in batch['stage']:continue
   data=gzip.decompress((Path(physics_run)/batch['gzip_path']).read_bytes())
   assert hashlib.sha256(data).hexdigest()==batch['raw_output_sha256']
   for r in json.loads(data)['results']:raw[r['id']]=r
  observed={}
  for i,c in enumerate(cases):
   r=raw[c['id']];f=r['frames'][-1]
   observed[i]=dict(frame=f['frame']+1,position=[f['x'],f['y']],events=dict(jump=r['jumps'],air_jump=r['air_jumps'],anchor_jump=r['anchor_jumps'],wall_jump=r['wall_jumps'],shot=r['shots'],hook_cast=r['grapples'],hook_contact=r['hook_contacts']))
 else:
  browser=json.loads((ROOT/'delivery/factory-v1/browser-public-v3/browser.json').read_text())
  observed={r['state']['selected']:r['state']for r in browser['records']if r['action']in ['replay_'+str(i)for i in range(len(cases))]}
 clips=[]
 sources={str(p.relative_to(ROOT)):sha(p)for p in [ROOT/'prototype/godot'/n for n in ('movie_factory.gd','movie_factory.tscn','main_factory.gd','main_v3.gd','dynamic_context.gd','lab_draw_v3.gd')]}
 for i,case in enumerate(cases):
  assert module_hash(case)==case['module_sha256']
  avi=out/f'sample-{i+1:02}.avi';log=out/f'record-{i+1:02}.log'
  if avi.exists()or log.exists():
   if not reuse or not(avi.exists()and log.exists()):raise ValueError('Keep previous evidence; choose another output directory')
  else:
   args=[str(ENGINE),'--path',str(ROOT/'prototype/godot'),'--audio-driver','Dummy','--write-movie',str(avi.resolve()),'--fixed-fps','60','res://movie_factory.tscn','--','--cases-json',str(cases_path),'--case',str(i)]
   with log.open('w')as f:subprocess.run(args,env=dict(os.environ,DISPLAY=display,LIBGL_ALWAYS_SOFTWARE='1'),stdout=f,stderr=subprocess.STDOUT,check=True,timeout=180)
  text=log.read_text();assert 'SCRIPT ERROR'not in text and 'ERROR:'not in text
  result=json.loads(next(line.split(' ',1)[1]for line in text.splitlines()if line.startswith('FACTORY_MOVIE_RESULT ')))
  assert result['module_sha256']==case['module_sha256']and result['candidate_uid']==case['factory_id']and result['case_id']==case['id']
  previous=observed[i]
  assert result['safe']and result['hp']==5 and result['stable_frames']>=6
  assert result['frame']==previous['frame']and result['events']==previous['events']and max(abs(a-b)for a,b in zip(result['position'],previous['position']))<.001
  mp4=out/f'sample-{i+1:02}.mp4'
  if mp4.exists():raise ValueError('Refuse existing encoded clip')
  with(out/f'encode-{i+1:02}.log').open('w')as f:subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdout=f,stderr=subprocess.STDOUT,check=True)
  probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]))
  clips.append(dict(sample=f'{i+1:02}',file=mp4.name,bytes=mp4.stat().st_size,sha256=sha(mp4),duration=float(probe['format']['duration']),module_sha256=case['module_sha256'],candidate_uid=case['factory_id'],engine_result=result,probe=probe))
  print(json.dumps(dict(sample=i+1,duration=clips[-1]['duration'],bytes=clips[-1]['bytes'],same_as_bound_physics_witness=True)),flush=True)
 concat=out/'concat.txt';concat.write_text(''.join("file '"+c['file']+"'\n"for c in clips));combined=out/'all-samples.mp4'
 if combined.exists():raise ValueError('Refuse existing compilation')
 with(out/'concat.log').open('w')as f:subprocess.run(['ffmpeg','-nostdin','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(combined)],stdout=f,stderr=subprocess.STDOUT,check=True)
 binding=dict(physics_run=str(Path(physics_run).relative_to(ROOT)),physics_binding_sha256=sha(Path(physics_run)/'source_binding.json'))if physics_run else dict(catalog_sha256=json.loads((ROOT/'delivery/factory-v1/web-release/catalog.json').read_text())['catalog_sha256'])
 manifest=dict(schema='pcg/video-review/v1',physics_hz=60,playback_speed=1,engine_sha256=sha(ENGINE),cases_sha256=sha(cases_path),evidence_binding=binding,source_files=sources,clips=clips,combined=dict(file=combined.name,bytes=combined.stat().st_size,sha256=sha(combined)),human_video_feedback=0,human_playtests=0,approved_offline=0,review_scope='Human video observations may guide geometry and pacing repair; no manual play or feel rating is claimed.')
 (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--out',required=True);p.add_argument('--display',default=':103');p.add_argument('--reuse-existing',action='store_true');p.add_argument('--cases');p.add_argument('--physics-run');a=p.parse_args();run(ROOT/a.out,a.display,a.reuse_existing,ROOT/a.cases if a.cases else None,ROOT/a.physics_run if a.physics_run else None)
