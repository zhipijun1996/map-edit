"""Native 60 Hz recordings with the existing exact trace comparison rules."""
import argparse,gzip,json,os,subprocess
from pathlib import Path
from .engine import ROOT,HERE
from ..factory.core.engine import ENGINE,file_sha
from ..factory.core.quality import module_hash
from pcg.tools.record_plains import event_key

KEYS=('frame','x','y','vx','vy','grounded','axis','requested','shot_charges','shot_cooldown','jumps_used','jump_maximum','energy','hp','traversal_state','real_velocity','normal_velocity','module_clock','moving_platforms','saws','support_id','goal_stable_frames')

def record(run_name,out_name,display=':103',families=None):
    source=ROOT/'results'/run_name;out=ROOT.parent/out_name
    if out.exists():raise ValueError('immutable_video_directory_exists')
    out.mkdir(parents=True);cases=json.loads((source/'review_cases.json').read_text())['cases']
    selected=[];seen=set()
    for c in cases:
        if c['family']in seen or families and c['family']not in families:continue
        seen.add(c['family']);selected.append(c)
    cases_path=out/'review_cases.json';cases_path.write_text(json.dumps(dict(cases=selected),ensure_ascii=False))
    batches=json.loads((source/'batches.json').read_text());clips=[]
    for i,c in enumerate(selected):
        assert module_hash(c)==c['module_sha256']
        ev=c['factory_evidence'];batch=next(b for b in batches if b['batch']==ev['batch']);packed=source/batch['gzip_path']
        assert file_sha(packed)==batch['gzip_sha256']
        raw=gzip.decompress(packed.read_bytes())
        import hashlib
        assert hashlib.sha256(raw).hexdigest()==batch['raw_output_sha256']
        r=json.loads(raw)['results'][ev['index']];assert r['id']==c['id']and r['ok']
        avi=out/(c['family']+'.avi');trace=out/(c['family']+'.trace.json');log=out/(c['family']+'.record.log')
        command=[str(ENGINE),'--path',str(ROOT/'prototype/godot'),'--audio-driver','Dummy','--write-movie',str(avi),'--fixed-fps','60',str(HERE/'main.tscn'),'--','--cases-json',str(cases_path),'--case',str(i),'--trace-json',str(trace)]
        (out/(c['family']+'.command.json')).write_text(json.dumps(command))
        with log.open('w')as f:subprocess.run(command,env=dict(os.environ,DISPLAY=display,LIBGL_ALWAYS_SOFTWARE='1'),stdout=f,stderr=subprocess.STDOUT,timeout=240,check=True)
        text=log.read_text();assert all(s not in text for s in ['ERROR:','SCRIPT ERROR','were leaked']),text[-4000:]
        native=json.loads(trace.read_text());assert native['module_sha256']==c['module_sha256']and native['case_id']==c['id']
        assert len(native['frames'])==len(r['frames']),(len(native['frames']),len(r['frames']))
        for a,b in zip(native['frames'],r['frames']):
            assert all(a[k]==b[k]for k in KEYS),[(k,a[k],b[k])for k in KEYS if a[k]!=b[k]]
            assert [event_key(e)for e in a['plains']['events']]==[event_key(e)for e in b['plains']['events']]
            assert a['plains']['bells']==b['plains']['bells']and a['plains']['enemies']==b['plains']['enemies']
            assert a['workshop']==b['workshop']
        mp4=out/(c['family']+'.mp4')
        with(out/(c['family']+'.encode.log')).open('w')as f:
            subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdout=f,stderr=subprocess.STDOUT,check=True)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]))
        assert probe['streams'][0]['avg_frame_rate']=='60/1'
        clips.append(dict(id=c['review_alias'],family=c['family'],file=mp4.name,sha256=file_sha(mp4),bytes=mp4.stat().st_size,
            duration=float(probe['format']['duration']),frames_exact=len(r['frames']),exact_fields=list(KEYS),
            cell_events_exact=True,reward_and_carrier_state_exact=True,case_sha256=c['module_sha256'],
            physics_binding_sha256=file_sha(source/'source_binding.json'),physics_run=str(source.relative_to(ROOT.parent)),
            native_trace_sha256=file_sha(trace),speed=1,human_fun='unreviewed'))
        print(json.dumps(clips[-1]),flush=True)
        # Only disposable newly generated AVI duplicates are removed after MP4
        # and exact native trace validation, not source attempts or failures.
        avi.unlink()
    manifest=dict(schema='pcg/video-review/v1',clips=clips,engine_sha256=file_sha(ENGINE),
        cases_sha256=file_sha(cases_path),end_hold_seconds=1,human_video_observation='unreviewed',human_playtest='unreviewed',production_admitted=False)
    (out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
    return out

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--out',required=True);p.add_argument('--display',default=':103');p.add_argument('--families',nargs='+');a=p.parse_args();record(a.run,a.out,a.display,a.families)
