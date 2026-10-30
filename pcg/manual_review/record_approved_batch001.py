"""Record exact canonical inputs with the existing strict native recorder."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import argparse
import gzip
import json
import subprocess
from pcg.migration import core, physics
from pcg.prototype.factory.core.quality import module_hash
from pcg.prototype.workshop.record import record, KEYS
from pcg.tools.record_plains import event_key


def review_only(run,out,case,reason):
    """Retain the original strict failure and enumerate every difference."""
    family=case['family'];log=out/(family+'.record.log')
    if any(s in log.read_text() for s in ('ERROR:','SCRIPT ERROR','were leaked')):
        raise ValueError('native_runtime_error_is_not_a_review_only_comparison')
    native=core.read(out/(family+'.trace.json'));e=case['factory_evidence']
    raw=json.loads(gzip.decompress((run/e['output']).read_bytes()))['results'][e['index']]
    differences=[]
    if len(native['frames'])!=len(raw['frames']):differences.append(dict(field='frame_count',native=len(native['frames']),physics=len(raw['frames'])))
    for a,b in zip(native['frames'],raw['frames']):
        for key in KEYS:
            if a[key]!=b[key]:differences.append(dict(frame=a['frame'],field=key,native=a[key],physics=b[key]))
        for key in ('bells','enemies'):
            if a['plains'][key]!=b['plains'][key]:differences.append(dict(frame=a['frame'],field='plains.'+key,native=a['plains'][key],physics=b['plains'][key]))
        av=[event_key(v)for v in a['plains']['events']];bv=[event_key(v)for v in b['plains']['events']]
        if av!=bv:differences.append(dict(frame=a['frame'],field='plains.events',native=av,physics=bv))
        if a['workshop']!=b['workshop']:differences.append(dict(frame=a['frame'],field='workshop',native=a['workshop'],physics=b['workshop']))
    core.write(out/'strict-comparison-failed.json',dict(passed=False,originalFailure=reason,normalization='Only original event_key projectile ObjectID suffix normalization',differences=differences))
    avi=out/(family+'.avi');mp4=out/(family+'.mp4')
    subprocess.run(['ffmpeg','-nostdin','-v','error','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]))
    assert probe['streams'][0]['avg_frame_rate']=='60/1'
    core.write(out/'manifest.json',dict(schema='pcg/video-review/v1',strict=False,reviewOnly=True,speed=1,
        clips=[dict(file=mp4.name,sha256=core.sha(mp4),bytes=mp4.stat().st_size,duration=float(probe['format']['duration']),frames=len(native['frames']))],
        physicsRun=core.relative(run),physicsBinding=physics.artifact(run/'source_binding.json'),cases=physics.artifact(out/'review_cases.json'),
        nativeTrace=physics.artifact(out/(family+'.trace.json')),comparison=physics.artifact(out/'strict-comparison-failed.json'),
        humanVideoObservation='UNKNOWN',humanPlaytest='UNKNOWN',productionApproval=False))
    avi.unlink()  # newly encoded duplicate only; trace/log/all differences retained


def main():
    p=argparse.ArgumentParser();p.add_argument('--ids',nargs='+',default=['01','02','04','05']);p.add_argument('--display',default=':99');p.add_argument('--version',default='v2');a=p.parse_args()
    for row in core.read(core.REPO/'feedback/manual-review/implementation-results/batch-001/authorization/handoff-v1.json')['rows']:
        rid=row['reviewId']
        if rid not in a.ids:continue
        run=core.REPO/'pcg/results'/('approved-b001-'+rid+'-canonical-v2');items=[]
        for entry in core.read(run/'canonical.json')['rows']:
            e=entry['evidence'];raw=json.loads(gzip.decompress((run/e['output']).read_bytes()))['results'][e['index']]
            c=core.read(run/'physics'/(e['batch']+'.input.json'))['cases'][e['index']]
            c=physics._recording(c,raw);c['factory_evidence']=e;c['review_alias']=rid+' / '+c['route_spec']['id'];c['module_sha256']=module_hash(c);items.append(c)
        core.write(run/'review_cases.json',dict(cases=items))
        scene='r01' if rid=='01' else 'r03' if rid=='03' else 'pair' if rid=='02' else 'r05' if rid=='05' and a.version=='v3' else 'plain'
        script_version='v2' if rid=='03' and a.version=='v3' else 'v1'
        output='feedback/manual-review/implementation-results/batch-001/videos/'+rid+'-'+a.version;out=core.REPO/output
        if out.exists():
            if (out/'manifest.json').exists():raise ValueError('immutable_video_already_finalized')
            review_only(run,out,items[0],'Original strict recorder stopped at first support_id mismatch; full differences enumerated here.')
        else:
            try:record(run.name,output,display=a.display,case_id=items[0]['id'],main_scene=core.REPO/'pcg/manual_review/runtime'/('approved_movie_'+scene+'_'+script_version+'.tscn'))
            except AssertionError as error:review_only(run,out,items[0],str(error))


if __name__=='__main__':main()
