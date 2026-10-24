"""Native full-world movies from real Router inputs; exact frame comparison."""
import argparse,gzip,hashlib,json,os,subprocess,shutil
from pathlib import Path
from ..director import REPO
from ..run import write
from pcg.prototype.factory.core.engine import ENGINE,PROJECT,file_sha


def run(physics_run,index,out,display=':103'):
    physics_run=Path(physics_run);out=Path(out)
    if out.exists():raise ValueError('immutable_movie_output_exists')
    out.mkdir(parents=True)
    original=json.loads((physics_run/'cases.json').read_text())['cases'][index]
    batches=json.loads((physics_run/'physics/batches.json').read_text())
    batch=batches[index];raw=gzip.decompress((physics_run/'physics'/batch['gzip_path']).read_bytes())
    if hashlib.sha256(raw).hexdigest()!=batch['raw_output_sha256']:raise ValueError('raw_trace_identity_mismatch')
    reference=json.loads(raw)['results'][0]
    if not reference['ok']:raise ValueError('cannot_sign_failed_movie_as_pass')
    case=dict(original);case['recorded_frames']=[{k:f[k]for k in ['frame','axis','requested','plan_index']}for f in reference['frames']]
    cases=out/'replay-cases.json';write(cases,{'cases':[case]})
    sources={}
    for p in Path(__file__).parent.rglob('*.gd'):
        rel=p.relative_to(REPO).as_posix();sources[rel]=file_sha(p)
        target=out/'source_snapshot'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
    write(out/'movie-source.json',dict(files=sources,engine_sha256=file_sha(ENGINE),case_sha256=file_sha(cases),
        physics_run=str(physics_run.relative_to(REPO)),physics_binding_sha256=file_sha(physics_run/'physics/source_binding.json')))
    trace=out/'native-trace.json';avi=out/'native.avi'
    command=[str(ENGINE),'--path',str(PROJECT),'--resolution','1280x720','--audio-driver','Dummy',
        '--write-movie',str(avi.resolve()),'--fixed-fps','60','--script',
        str(Path(__file__).parent/'godot/r2_movie_runner.gd'),'--','--cases-json',str(cases.resolve()),
        '--case','0','--movie','--trace-json',str(trace.resolve())]
    write(out/'command.json',command)
    with (out/'engine.log').open('w')as log:
        completed=subprocess.run(command,env=dict(os.environ,DISPLAY=display,LIBGL_ALWAYS_SOFTWARE='1'),
            stdout=log,stderr=subprocess.STDOUT,timeout=900)
    native=json.loads(trace.read_text())['result']
    comparison=dict(native_exit_code=completed.returncode,reference_frames=len(reference['frames']),native_frames=len(native['frames']),mismatches=[])
    keys=['frame','x','y','vx','vy','grounded','axis','requested','shot_charges','shot_cooldown','jumps_used',
        'energy','hp','traversal_state','real_velocity','normal_velocity','module_clock','moving_platforms','saws',
        'support_id','goal_stable_frames','plains','plains_events_delta','player_damage_delta']
    for left,right in zip(native['frames'],reference['frames']):
        different=[k for k in keys if left.get(k)!=right.get(k)]
        if different:comparison['mismatches'].append(dict(frame=left['frame'],fields=different))
    log=(out/'engine.log').read_text()
    comparison['passed']=completed.returncode==0 and native['ok'] and len(native['frames'])==len(reference['frames'])and not comparison['mismatches']and'ERROR:'not in log and'SCRIPT ERROR'not in log
    comparison['fields']=keys;write(out/'comparison.json',comparison)
    if not comparison['passed']:raise ValueError('native_movie_does_not_match_bound_physics; evidence retained')
    mp4=out/'full-route.mp4'
    with(out/'encode.log').open('w')as log:
        subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-preset','fast','-crf','23',
            '-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdout=log,stderr=subprocess.STDOUT,check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]))
    if probe['streams'][0]['avg_frame_rate']!='60/1':raise ValueError('wrong_movie_frame_rate')
    write(out/'manifest.json',dict(schema='pcg/full-r2-native-video/v1',case_id=case['id'],
        file=mp4.name,bytes=mp4.stat().st_size,sha256=file_sha(mp4),duration=float(probe['format']['duration']),
        physics_hz=60,playback_speed=1,native_trace_sha256=file_sha(trace),comparison=comparison,
        scope='Complete real route at normal speed; boot/warmup and one final second retained, read-only full-map minimap',
        human_fun='unverified',human_playtests=0))
    print(json.dumps(dict(out=str(out),frames=len(native['frames']),duration=probe['format']['duration'],exact=True)),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',type=Path,required=True);p.add_argument('--index',type=int,required=True)
    p.add_argument('--out',type=Path,required=True);p.add_argument('--display',default=':103')
    a=p.parse_args();run(a.run.resolve(),a.index,a.out.resolve(),a.display)
