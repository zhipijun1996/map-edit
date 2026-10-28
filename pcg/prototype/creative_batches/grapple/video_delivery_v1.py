"""Index strict native clips, inspect metadata, and concatenate complete attempts."""
import json,subprocess
from pathlib import Path
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import file_sha
if __name__=='__main__':
 out=ROOT/'results/workshop-creative-grapple-videos-v2';idx=json.loads((out/'index.json').read_text());mods={r['recipe']:r for r in json.loads((ROOT/'results/workshop-creative-grapple-delivery-v1/summary-v2.json').read_text())['modules']};clips=[];elapsed=0.
 for row in idx['rows']:
  assert row['status']=='exact_native_recording_pass';c=row['clips'][0];p=out/row['recipe']/c['file'];assert file_sha(p)==c['sha256'];probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(p)]));assert probe['streams'][0]['avg_frame_rate']=='60/1'
  # The transparency revision changed only presentation, with identical replay traces.
  assert file_sha(out/row['recipe']/('grapple-'+row['recipe']+'.trace.json'))==file_sha(ROOT/'results/workshop-creative-grapple-videos-v1'/row['recipe']/('grapple-'+row['recipe']+'.trace.json'))
  clips.append(dict(recipe=row['recipe'],mp4=str(p.relative_to(ROOT.parent)),sha256=file_sha(p),bytes=p.stat().st_size,duration_seconds=float(probe['format']['duration']),contentVersion=mods[row['recipe']]['contentVersion'],module_json=mods[row['recipe']]['json'],case_sha256=c['case_sha256'],native_trace_sha256=c['native_trace_sha256'],strict_frames=c['frames_exact'],strict_fields=c['exact_fields'],strict_cell_events=True,strict_reward_carrier_state=True,manifest=row['manifest'],combined_start_seconds=elapsed,preview=str((out/row['recipe']/'preview-v1.png').relative_to(ROOT.parent)),visual_inspection='one extracted frame inspected by model; title and action visible, no human review'))
  elapsed+=float(probe['format']['duration'])
 concat=out/'concat-v1.txt';concat.write_text(''.join("file '"+str((ROOT.parent/c['mp4']).resolve())+"'\n"for c in clips));combined=out/'four-grapple-relationships-v1.mp4'
 with(out/'concat-v1.log').open('w')as f:subprocess.run(['ffmpeg','-nostdin','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(combined)],stdout=f,stderr=subprocess.STDOUT,check=True)
 probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(combined)]));assert probe['streams'][0]['avg_frame_rate']=='60/1'
 report=dict(schema='pcg/grapple-video-delivery/v1',clips=clips,strict_passed=4,strict_frames=sum(c['strict_frames']for c in clips),combined=dict(mp4=str(combined.relative_to(ROOT.parent)),sha256=file_sha(combined),bytes=combined.stat().st_size,duration_seconds=float(probe['format']['duration']),editing='four complete attempts concatenated in listed order; three explicit segment boundaries; original timing unchanged; each ends in one second frozen completion'),recording_index=str((out/'index.json').relative_to(ROOT.parent)),recording_index_sha256=file_sha(out/'index.json'),source_script=str(Path(__file__).relative_to(ROOT.parent)),source_script_sha256=file_sha(__file__),human_video_observation='unreviewed',manual_play='unreviewed',production_admitted=False)
 (out/'delivery-v1.json').write_text(json.dumps(report,ensure_ascii=False,indent=2));print(json.dumps(dict(clips=4,exact_frames=report['strict_frames'],duration=report['combined']['duration_seconds'],combined=str(combined)),ensure_ascii=False))
