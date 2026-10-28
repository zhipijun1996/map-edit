"""Add explicit replay/scene evidence paths; never rewrite prior versions."""
import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];REPO=ROOT.parent

def main():
 out=ROOT/'results/workshop-creative-machinery-delivery-v19';out.mkdir(exist_ok=False)
 d=json.loads((ROOT/'results/workshop-creative-machinery-delivery-v18/manifest.json').read_text());d['schema']='pcg/creative-machinery-delivery/v19'
 for row in d['candidates']:
  media=REPO/row['video'];directory=media.parent;manifest=json.loads((directory/'manifest.json').read_text());clip=manifest['clips'][0];command=json.loads((directory/(row['family']+'.command.json')).read_text());scene=next(x for x in command if x.endswith('.tscn'))
  row.update(video_manifest=str((directory/'manifest.json').relative_to(REPO)),native_record_log=str((directory/(row['family']+'.record.log')).relative_to(REPO)),native_trace=str((directory/(row['family']+'.trace.json')).relative_to(REPO)),native_trace_sha256=clip['native_trace_sha256'],canonical_case_sha256=clip['case_sha256'],native_command=str((directory/(row['family']+'.command.json')).relative_to(REPO)),main_scene=str(Path(scene).relative_to(REPO)),precise_comparison=dict(frames=clip['frames_exact'],fields=clip['exact_fields'],cell_events_exact=clip['cell_events_exact'],reward_and_carrier_state_exact=clip['reward_and_carrier_state_exact'],physics_binding_sha256=clip['physics_binding_sha256']),case_file=str((directory/'review_cases.json').relative_to(REPO)))
 d['strict_candidates']=[x['family']for x in d['candidates']if x['independent_relationship_candidate']];d['additional_adaptation']='elevator-headroom';d['machinery_headless_engine_running']=False;d['recording_scene_note']='First four native clips use workshop/main.tscn; dual-service uses dock_main_v17.tscn extending dock_main_v15.gd and original workshop/main.gd.'
 p=Path(__file__);d['source_files'].append(dict(path=str(p.relative_to(REPO)),sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
 (out/'manifest.json').write_text(json.dumps(d,ensure_ascii=False,indent=2));print(str(out/'manifest.json'))
if __name__=='__main__':main()
