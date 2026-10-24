"""Read-only audit of frozen outputs, original code and the review playlist."""
import gzip,hashlib,json,collections
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def summarize():
 project=ROOT/'prototype/godot';original=json.loads((project/'source_provenance.json').read_text())['files']
 assert all(sha(project/p)==v for p,v in original.items())
 additions=json.loads((ROOT/'research/plains-runtime-additions.json').read_text())['files'];assert all(sha(project/p)==v['sha256']for p,v in additions.items())
 runs=[]
 for run in sorted((ROOT/'results').glob('plains-*')):
  outputs=list((run/'physics').glob('*.output.json'));results=[r for p in outputs for r in json.loads(p.read_text())['results']]
  registered=json.loads((run/'batches.json').read_text())if(run/'batches.json').exists()else[]
  results += [r for b in registered for r in json.loads(gzip.decompress((run/b['gzip_path']).read_bytes()))['results']]
  costs=[json.loads(p.read_text())for p in(run/'physics').glob('*.execution.json')]
  runs.append(dict(run=run.name,raw_returned_cases=len(results),rejected_definitions=sum(r.get('reason')=='rejected_module_definition'for r in results),accepted_batches=len(registered),complete_summary=(run/'summary.json').exists(),wall_seconds=sum(c['wall_seconds']for c in costs),child_cpu_seconds=sum(c['child_cpu_seconds']for c in costs),peak_child_rss_kib=max((c['children_peak_rss_kib']for c in costs),default=0),scope='Returned outputs include rejection and failed batches; not all count as accepted physical validation'))
 review=ROOT/'results/plains-review-v1';playlist=json.loads((review/'playlist.json').read_text());cases=json.loads((review/'review_cases.json').read_text())['cases'];details=[]
 for c,sample in zip(cases,playlist['samples']):
  run=ROOT/sample['source_run'];r=next(r for b in json.loads((run/'batches.json').read_text())if 'holdout'in b['stage']for r in json.loads(gzip.decompress((run/b['gzip_path']).read_bytes()))['results']if r['id']==c['id']);frames=r['frames'];extra={}
  for saw in c.get('saws',[]):
   x=saw['origin'][0];cross=next((f for a,f in zip(frames,frames[1:])if a['x']<x<=f['x']),None)
   last_land=next((f['frame']for a,f in zip(frames,frames[1:])if not a['grounded']and f['grounded']),None)
   recovered=[f for f in frames if last_land is not None and last_land<=f['frame']and f['x']<x-40 and f['grounded']and abs(f['real_velocity'][0])<1]
   extra=dict(landing_frame=last_land,supported_stationary_frames_before_gear=len(recovered),grounded_at_crossing=cross['grounded']if cross else None,gear_crossing_frame=cross['frame']if cross else None,gear_crossing_state=cross['saws']if cross else None,interpretation='Measured supported pause and ground crossing, not a proof that waiting is always necessary')
  details.append(dict(alias=sample['alias'],candidate_uid=c['factory_id'],module_sha256=c['module_sha256'],source_run=sample['source_run'],ticks=r['ticks'],hp=r['hp'],shots=r['shots'],jumps=r['jumps'],advanced=dict(air_jumps=r['air_jumps'],wall_jumps=r['wall_jumps'],grapples=r['grapples']),actual_decision_evidence=extra,cell_events=r['plains']['events']))
 summary=dict(schema='pcg/plains-audit/v1',protected_original_files_unchanged=len(original),additional_original_art_files=len(additions),runs=runs,representatives=details,human_video_feedback=0,human_playtests=0,approved_offline=0)
 (review/'audit.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2));print(json.dumps(dict(runs=runs,protected=len(original)),ensure_ascii=False,indent=2))
if __name__=='__main__':summarize()
