"""Explicit viewing excerpts; preserve complete strictly compared recordings."""
import hashlib,json,math,subprocess,gzip
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
    cases=json.loads((folder/'review_cases.json').read_text())['cases'];case=next(c for c in cases if c['module_sha256']==source['case_sha256'])
    run=ROOT/source['physics_run'];ev=case['factory_evidence']
    batch=next(b for b in json.loads((run/'batches.json').read_text())if b['batch']==ev['batch'])
    packed=run/batch['gzip_path'];assert sha(packed)==batch['gzip_sha256']
    raw=gzip.decompress(packed.read_bytes());assert hashlib.sha256(raw).hexdigest()==batch['raw_output_sha256']
    result=json.loads(raw)['results'][ev['index']];assert result['id']==case['id']
    last_action=max(v['frame']for v in result['fired_commands'])
    assert last_action+30<kept
    state=['x','y','vx','vy','hp','shot_charges','shot_cooldown','jumps_used','energy']
    assert all([f[k]for k in state]==[frames[-1][k]for k in state]for f in frames[kept:])
    target=OUT/(name+'-excerpt.mp4')
    prior=json.loads((OUT/'manifest.json').read_text())
    old=next(c for c in prior['clips']if c['file']==target.name)
    assert target.exists()and sha(target)==old['sha256']
    vf='drawtext=fontfile=/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc:textfile='+str(label)+':x=20:y=h-42:fontsize=20:fontcolor=white:box=1:boxcolor=black@0.8:boxborderw=6'
    if not target.exists():subprocess.run(['ffmpeg','-v','error','-nostdin','-i',str(movie),'-frames:v',str(kept),'-vf',vf,'-an','-c:v','libx264','-crf','23','-pix_fmt','yuv420p','-movflags','+faststart',str(target)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(target)]))
    assert probe['streams'][0]['avg_frame_rate']=='60/1'
    rows.append(dict(file=target.name,sha256=sha(target),duration=float(probe['format']['duration']),
        source_full_movie=str(movie.relative_to(ROOT)),source_sha256=sha(movie),source_trace_sha256=sha(trace),
        case_id=json.loads(trace.read_text())['case_id'],case_sha256=source['case_sha256'],
        kept_movie_prefix_frames=kept,first_thirty_stable_frame=stable,last_accepted_action_frame=last_action,
        removed='Only later verification idle tail; full native movie and its strict comparison remain separate',
        added='Explicit excerpt label',speed=1,qualification='Viewing excerpt; not a new physical recording or Module witness'))
target=OUT/'manifest-v2.json';assert not target.exists()
target.write_text(json.dumps(dict(schema='pcg/video-viewing-excerpts/v2',clips=rows,new_physics_cases=0,supersedes='manifest.json',correction='Initial audit queried accepted actions on the native projection which omits them. Current audit reads actual original fired_commands; movie bytes and retained prefix unchanged.',
    source_builder_sha256=sha(Path(__file__)),human_video_observation='UNKNOWN',production_admitted=False),ensure_ascii=False,indent=2)+'\n')
print(json.dumps(rows,ensure_ascii=False))
