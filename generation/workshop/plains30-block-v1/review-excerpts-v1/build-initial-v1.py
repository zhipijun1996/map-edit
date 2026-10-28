"""Explicit viewing excerpts; preserve complete strictly compared recordings."""
import hashlib,json,math,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
label=OUT/'label.txt'
if not label.exists():label.write_text('审阅节选：省略抵达后的验收停留；完整原片另存',encoding='utf-8')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
rows=[]
for name in ['BA2-forward-v1','BA2-return-v1']:
    folder=OUT.parent/'videos'/name
    source=json.loads((folder/'manifest.json').read_text())['clips'][0]
    movie=folder/source['file'];assert sha(movie)==source['sha256']
    trace=folder/(source['family']+'.trace.json');assert sha(trace)==source['native_trace_sha256']
    frames=json.loads(trace.read_text())['frames']
    stable=next(f['frame']for f in frames if f['goal_stable_frames']>=30)
    # Keep an additional second of stable real world after that observation.
    # Round up and retain ample startup/teardown allowance; no action is cut.
    seconds=math.ceil((stable+66)/60);kept=seconds*60
    assert kept<len(frames)
    last_action=max((f['frame']for f in frames if f.get('accepted')),default=0)
    assert last_action+30<kept
    state=['x','y','vx','vy','hp','shot_charges','shot_cooldown','jumps_used','energy']
    assert all([f[k]for k in state]==[frames[-1][k]for k in state]for f in frames[kept:])
    target=OUT/(name+'-excerpt.mp4');assert not target.exists()
    vf='drawtext=fontfile=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc:textfile='+str(label)+':x=20:y=h-42:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.8:boxborderw=6'
    subprocess.run(['ffmpeg','-v','error','-nostdin','-i',str(movie),'-frames:v',str(kept),'-vf',vf,'-an','-c:v','libx264','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(target)]))
    assert probe['streams'][0]['avg_frame_rate']=='60/1'
    rows.append(dict(file=target.name,sha256=sha(target),duration=float(probe['format']['duration']),
        source_full_movie=str(movie.relative_to(ROOT)),source_sha256=sha(movie),source_trace_sha256=sha(trace),
        case_id=json.loads(trace.read_text())['case_id'],case_sha256=source['case_sha256'],
        kept_movie_prefix_frames=kept,first_thirty_stable_frame=stable,last_accepted_action_frame=last_action,
        removed='Only later verification idle tail; full native movie and its strict comparison remain separate',
        added='Explicit excerpt label',speed=1,qualification='Viewing excerpt; not a new physical recording or Module witness'))
target=OUT/'manifest.json';assert not target.exists()
target.write_text(json.dumps(dict(schema='pcg/video-viewing-excerpts/v1',clips=rows,new_physics_cases=0,
    source_builder_sha256=sha(Path(__file__)),human_video_observation='UNKNOWN',production_admitted=False),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(rows,ensure_ascii=False))
