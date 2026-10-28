"""Delegate root branch-port witnesses to the unchanged original recorder.

Failure is recorded, never relaxed. A stable original movie may separately be
encoded as review-only when exact comparison fails.
"""
import argparse,json,subprocess,traceback
from pathlib import Path
from pcg.prototype.workshop.record import record
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
REPO=ROOT.parent

def record_one(run,cid):
 out=REPO/'generation/workshop/plains50-ports-v1/videos'/cid
 try:
  record(run,str(out.relative_to(REPO)),display=':114',case_id=cid)
  return dict(case_id=cid,source_run='pcg/results/'+run,status='strict_pass',manifest=str((out/'manifest.json').relative_to(REPO)),manifest_sha256=file_sha(out/'manifest.json'))
 except Exception as exc:
  error=dict(case_id=cid,source_run='pcg/results/'+run,status='record_or_strict_failure',error_type=type(exc).__name__,error=str(exc),traceback=traceback.format_exc(),review_only=False)
  out.mkdir(parents=True,exist_ok=True)
  for avi in out.glob('*.avi'):
   log=avi.with_suffix('.record.log');trace=avi.with_suffix('.trace.json')
   if not log.exists()or not trace.exists():continue
   result=None
   for line in log.read_text().splitlines():
    if line.startswith('WORKSHOP_MOVIE_RESULT '):
     try:result=json.loads(line.removeprefix('WORKSHOP_MOVIE_RESULT '))
     except json.JSONDecodeError:pass
   if not result or not result.get('safe')or result.get('hp')!=5 or result.get('stable_frames',0)<6:continue
   mp4=avi.with_suffix('.review-only.mp4')
   with mp4.with_suffix('.encode.log').open('w')as f:subprocess.run(['ffmpeg','-nostdin','-i',str(avi),'-an','-c:v','libx264','-preset','medium','-crf','24','-pix_fmt','yuv420p','-movflags','+faststart',str(mp4)],stdout=f,stderr=subprocess.STDOUT,check=True)
   error.update(status='strict_failed_review_only',review_only=True,file=str(mp4.relative_to(REPO)),sha256=file_sha(mp4),native_trace=str(trace.relative_to(REPO)),native_trace_sha256=file_sha(trace),movie_result=result)
  p=out/'strict-failure.json';p.write_text(json.dumps(error,ensure_ascii=False,indent=2)+'\n');return error

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--recipe',required=True);p.add_argument('--cases',nargs='+');a=p.parse_args();run='workshop-plains50-ports-production-v1/'+a.recipe;source=ROOT/'results'/run/'review_cases.json';cs=json.loads(source.read_text())['cases'];ids=a.cases or[c['id']for c in cs];rows=[]
 for cid in ids:
  row=record_one(run,cid);rows.append(row);print(json.dumps(row,ensure_ascii=False),flush=True)
 out=REPO/'generation/workshop/plains50-ports-v1/videos'/(a.recipe+'-recording-index-v1.json')
 if out.exists():raise ValueError('immutable_recording_index_exists')
 out.write_text(json.dumps(dict(schema='pcg/ports-native-review-index/v1',recording_wrapper=dict(path=str(Path(__file__).relative_to(REPO)),sha256=file_sha(Path(__file__))),source_cases=dict(path=str(source.relative_to(REPO)),sha256=file_sha(source)),clips=rows,production_admitted=False,human_video_observation='unreviewed'),ensure_ascii=False,indent=2)+'\n')
