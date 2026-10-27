"""Enumerate an existing strict failure, never relax the original comparator.

Only support-ID-only differences may become explicitly review-only clips.
Uses the original field list and event normalization; no physical admission.
"""
import argparse,gzip,json,hashlib,subprocess
from pathlib import Path
from pcg.prototype.workshop.record import KEYS
from pcg.tools.record_plains import event_key
from pcg.prototype.factory.core.engine import file_sha

REPO=Path(__file__).resolve().parents[4]

def audit(run,folder,version,extra=()):
    source=REPO/'pcg/results'/run;out=Path(folder).resolve()
    target=out/'review-only-manifest.json'
    if target.exists():raise ValueError('immutable_review_manifest_exists')
    cases=json.loads((out/'review_cases.json').read_text())['cases']
    if len(cases)!=1:raise ValueError('one_exact_failed_recording_required')
    c=cases[0];family=c['family'];trace=out/(family+'.trace.json')
    native=json.loads(trace.read_text())
    batch=next(b for b in json.loads((source/'batches.json').read_text())if b['batch']==c['factory_evidence']['batch'])
    packed=source/batch['gzip_path'];assert file_sha(packed)==batch['gzip_sha256']
    raw=gzip.decompress(packed.read_bytes());assert hashlib.sha256(raw).hexdigest()==batch['raw_output_sha256']
    result=json.loads(raw)['results'][c['factory_evidence']['index']]
    assert native['module_sha256']==c['module_sha256']and native['case_id']==result['id']==c['id']
    assert len(native['frames'])==len(result['frames'])
    differences=[]
    def compare(frame,key,a,b):
        if a!=b:differences.append(dict(frame=frame,field=key,native=a,physics=b))
    for a,b in zip(native['frames'],result['frames']):
        for key in (*KEYS,*extra):compare(a['frame'],key,a[key],b[key])
        for key in ['bells','enemies']:compare(a['frame'],'plains.'+key,a['plains'][key],b['plains'][key])
        compare(a['frame'],'plains.events',[event_key(e)for e in a['plains']['events']],[event_key(e)for e in b['plains']['events']])
        compare(a['frame'],'workshop',a['workshop'],b['workshop'])
    report=dict(schema='pcg/native-strict-failure-audit/v2',strict_comparison='failed',
        case_id=c['id'],case_sha256=c['module_sha256'],contentVersion=version,
        frames_compared=len(result['frames']),all_differences=differences,
        extra_fields_compared=list(extra),extra_fields_exact=not any(d['field']in extra for d in differences),
        physics_run=str(source.relative_to(REPO)),physics_binding_sha256=file_sha(source/'source_binding.json'),
        native_trace_sha256=file_sha(trace),auditor_source_sha256=file_sha(Path(__file__)),
        original_comparator_unchanged=True,production_admitted=False)
    audit_path=out/'strict-failure-audit-v1.json'
    if audit_path.exists():raise ValueError('immutable_audit_exists')
    audit_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    if not differences or {d['field']for d in differences}!={'support_id'}:
        raise ValueError('not_a_support_identity_only_failure; diagnostic retained, no review publication')
    movie=out/(family+'-review-only.mp4')
    if movie.exists():raise ValueError('immutable_movie_exists')
    with(out/'review-only-encode.log').open('w')as log:
        subprocess.run(['ffmpeg','-nostdin','-i',str(out/(family+'.avi')),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(movie)],stdout=log,stderr=subprocess.STDOUT,check=True)
    probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(movie)]))
    assert probe['streams'][0]['avg_frame_rate']=='60/1'
    clip=dict(file=movie.name,sha256=file_sha(movie),bytes=movie.stat().st_size,
        duration=float(probe['format']['duration']),fps='60/1',speed=1,contentVersion=version,
        case_id=c['id'],case_sha256=c['module_sha256'],strict_comparison='failed',frames_exact=False,
        frames_compared=len(result['frames']),all_differences=differences,
        extra_fields_compared=list(extra),extra_fields_exact=report['extra_fields_exact'],
        audit=dict(path=str(audit_path.relative_to(REPO)),sha256=file_sha(audit_path)),
        physics_run=report['physics_run'],native_trace_sha256=file_sha(trace))
    value=dict(schema='pcg/video-review-only/v1',clips=[clip],review_cases_sha256=file_sha(out/'review_cases.json'),
        end_hold_seconds=1,human_video_observation='UNKNOWN',human_playtest='UNKNOWN',production_admitted=False,
        note='Original strict comparison failed. Every difference is retained; extra observers do not override the failure.')
    target.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(review_only=True,frames=len(result['frames']),differences=len(differences),extra_fields_exact=report['extra_fields_exact'],movie=str(movie.relative_to(REPO)))))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--video-dir',type=Path,required=True)
    p.add_argument('--content-version',required=True);p.add_argument('--extra',nargs='*',default=[])
    a=p.parse_args();audit(a.run,a.video_dir,a.content_version,a.extra)
