"""Publish genuine native review films WITH their failed strict comparisons.

The original recorder/comparator is not relaxed. These clips cannot be counted
as all-field exact films; their completion receipts and every discrepancy ship.
"""
import argparse,gzip,json,subprocess
from pathlib import Path
from .engine import ROOT
from .experiments import write
from .record import KEYS
from ..factory.core.engine import file_sha

def run(out_name):
    dest=ROOT.parent/out_name
    if dest.exists():raise ValueError('immutable_macro_media_delivery')
    dest.mkdir(parents=True);clips=[]
    for label,source in [('M01','workshop-macro-holdout-v2'),('M02','workshop-macro-holdout-v2'),('M03','workshop-macro-retry-held-v2')]:
        raw=ROOT/'results/workshop-macro-media-v2'/label
        c=json.loads((raw/'review_cases.json').read_text())['cases'][0];ev=c['factory_evidence'];run=ROOT/'results'/source
        b=next(b for b in json.loads((run/'batches.json').read_text())if b['batch']==ev['batch'])
        r=json.loads(gzip.decompress((run/b['gzip_path']).read_bytes()))['results'][ev['index']]
        native=json.loads((raw/'gate-brake-return.trace.json').read_text());nf=native['frames']
        assert len(nf)==len(r['frames'])and native['module_sha256']==c['module_sha256']
        differences=[]
        for a,bf in zip(nf,r['frames']):
            for k in KEYS:
                if a[k]!=bf[k]:differences.append(dict(frame=a['frame'],field=k,native=a[k],batch=bf[k]))
            for k in ['plains','workshop']:
                if a[k]!=bf[k]:differences.append(dict(frame=a['frame'],field=k,native=a[k],batch=bf[k]))
        log=(raw/'gate-brake-return.record.log').read_text()
        result=json.loads(next(line.split('WORKSHOP_MOVIE_RESULT ',1)[1]for line in log.splitlines()if 'WORKSHOP_MOVIE_RESULT 'in line))
        assert result['safe']and result['hp']==5 and result['stable_frames']>=6
        assert not any(s in log for s in ['ERROR:','SCRIPT ERROR','were leaked'])
        avi=raw/'gate-brake-return.avi';mp4=dest/(label+'.mp4')
        with(raw/'review-encode.log').open('w')as f:subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-crf','24','-preset','medium','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdout=f,stderr=subprocess.STDOUT,check=True)
        probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(mp4)]));assert probe['streams'][0]['avg_frame_rate']=='60/1'
        clips.append(dict(id=label,file=mp4.name,sha256=file_sha(mp4),bytes=mp4.stat().st_size,duration=float(probe['format']['duration']),fps='60/1',speed=1,
            case_id=c['id'],case_sha256=c['module_sha256'],variant=c['rule_parameters']['variant'],physics_run=source,raw_native_directory=str(raw.relative_to(ROOT.parent)),native_trace_sha256=file_sha(raw/'gate-brake-return.trace.json'),
            strict_comparison='failed'if differences else'passed',differences=differences,native_completion=result,review_only=True,human_video_observation='unreviewed'))
        print(json.dumps(dict(id=label,frames=len(nf),differences=len(differences),fields=sorted({d['field']for d in differences}))),flush=True)
    listing=dest/'concat.txt';listing.write_text(''.join("file '"+str((dest/c['file']).resolve())+"'\n"for c in clips))
    subprocess.run(['ffmpeg','-nostdin','-f','concat','-safe','0','-i',str(listing),'-c','copy','-movflags','+faststart',str(dest/'overview.mp4')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
    write(dest/'manifest.json',dict(schema='pcg/workshop-macro-video-review/v1',clips=clips,overview=dict(file='overview.mp4',sha256=file_sha(dest/'overview.mp4'),concatenation='M01 -> M02 -> M03, no intra-clip edits, original 1x, 1 second final freeze per clip'),
        exact_video_count=sum(c['strict_comparison']=='passed'for c in clips),human_playtest=False,production_admitted=False))
    listing.unlink();return dest

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',required=True);a=p.parse_args();run(a.out)
