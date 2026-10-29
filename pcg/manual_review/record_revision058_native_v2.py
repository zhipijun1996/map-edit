"""Real rendered replay of compiled native scenes; failed workshop films remain preserved."""
import json,os,subprocess,sys
from pcg.migration import core,physics
from .continue_revision058_v1 import rows,label,OUT
from .finalize_revision058_v1 import folder_for

def run(row):
 n=label(row);f=folder_for(row);cases=core.read(f/'playable/cases.json')['cases'];wanted={'42':'C-to-exit','s02':'B-to-T','s07':'L-to-T','s09':'B-to-L','s11':'B-to-R','s12':'B-to-T','s15':'L-to-R'}.get(n,cases[0]['route_spec']['id']);i=next(i for i,c in enumerate(cases)if c['route_spec']['id']==wanted);c=cases[i]
 out=OUT/'videos'/('native-'+n+'-'+wanted+('-v2'if n=='42'else'-v1'));assert not out.exists();out.mkdir(parents=True);avi=out/'native.avi';receipt=out/'native-receipt.json';scene=core.REPO/('pcg/manual_review/runtime/revision058_native_movie42_v1.tscn'if n=='42'else'pcg/manual_review/runtime/revision058_native_movie_v1.tscn');engine=core.REPO/'pcg/toolchain/Godot_v4.7.2-stable_linux.x86_64';command=[str(engine),'--path',str(core.REPO/'pcg/prototype/godot'),'--audio-driver','Dummy','--write-movie',str(avi),'--fixed-fps','60',str(scene),'--','--native-scene',str(f/'playable/demo.tscn'),'--verify-package','--case',str(i),'--receipt',str(receipt)];core.write(out/'command.json',command)
 with(out/'native.record.log').open('w')as stream:p=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'DISPLAY':':104','LIBGL_ALWAYS_SOFTWARE':'1'},timeout=360)
 text=(out/'native.record.log').read_text();assert p.returncode==0 and all(t not in text for t in ['SCRIPT ERROR','ERROR:','were leaked']),text[-2500:]
 actual=core.read(receipt);assert actual['passed']and actual['hp']==5 and not actual['damage']and not actual['returns'];expected=core.read(f/'playable/load-evidence'/('case-'+str(i))/'receipt.json');assert actual['case_id']==expected['case_id']and actual['actual_frames']==expected['actual_frames'];strict=actual['frames']==expected['frames'];differences=[]
 for a,b in zip(actual['frames'],expected['frames']):
  if a!=b: differences.append(dict(frame=a['frame'],fields=[k for k in sorted(set(a)|set(b))if a.get(k)!=b.get(k)]))
 core.write(out/'strict-diff.json',dict(strict=strict,rawFrameEquality=True,changedFrames=len(differences),rows=differences,headlessReference=physics.artifact(f/'playable/load-evidence'/('case-'+str(i))/'receipt.json'),nativeOutcomePassed=True,comparisonNotRelaxed=True))
 mp4=out/'native.mp4'
 with(out/'encode.log').open('w')as stream:subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdout=stream,stderr=subprocess.STDOUT,check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]));core.write(out/'media-probe.json',probe);assert probe['streams'][0]['avg_frame_rate']=='60/1';duration=float(probe['format']['duration']);assert abs(duration-(actual['actual_frames']+int(c.get('warmup_frames',4)))/60-1)<.15
 core.write(out/'manifest.json',dict(schema='pcg/video-review/v1',clips=[dict(file='native.mp4',id=n+' / '+wanted,sha256=core.sha(mp4),duration=duration,frames_exact=actual['actual_frames'],speed=1)],strict=strict,reviewOnly=not strict,nativeOutcomePassed=True,nativeReceipt=physics.artifact(receipt),strictDiff=physics.artifact(out/'strict-diff.json'),end_hold_seconds=1,scope=dict(base_module_id=row['moduleId'],designVersion=row['designVersion'],contentVersion=core.read(f/'module.mapnote.json')['generationContract']['contentVersion'],route=c['route_spec'],compiledPlayableScene=physics.artifact(f/'playable/demo.tscn'),actualLauncher=physics.artifact(scene),presentationOnly=physics.artifact(scene.with_suffix('.gd')),engine=physics.artifact(engine),speed=1,endHoldSeconds=1,editorialCuts=[],humanPlaytest='UNKNOWN',productionApproval=False),supersedes='Earlier workshop-consumer film; failed replay/strict comparison is preserved and never used as proof of native scene completion.'))
 avi.unlink();print(n,'ACTUAL_NATIVE_MOVIE_PASS','STRICT'if strict else'REVIEW_ONLY',actual['actual_frames'],flush=True)
if __name__=='__main__':
 for r in rows():
  if not sys.argv[1:]or label(r)in sys.argv[1:]:run(r)
