"""Resolve the persisted native consumer, then call the original strict recorder."""
import argparse,json
from pathlib import Path
from pcg.prototype.workshop.record import record,ROOT
from pcg.prototype.factory.core.engine import file_sha

def main():
    p=argparse.ArgumentParser();p.add_argument('--run',required=True);p.add_argument('--out',required=True)
    p.add_argument('--case-id',required=True);p.add_argument('--display',default=':115');a=p.parse_args()
    bundle=ROOT/'results'/a.run/'review_cases.json'
    case=next(c for c in json.loads(bundle.read_text())['cases']if c['id']==a.case_id)
    scene=Path(case['native_block_scene'])
    if not scene.is_absolute():scene=ROOT.parent/scene
    if not scene.is_file():raise ValueError('persisted_native_consumer_missing/'+str(scene))
    binding=dict(case_id=a.case_id,bundle_sha256=file_sha(bundle),scene=str(scene.relative_to(ROOT.parent)),
        scene_sha256=file_sha(scene),script_sha256=file_sha(scene.with_suffix('.gd')),
        consumer_selection='Exact persisted case.native_block_scene, no guessed directory or fallback',original_recorder_unchanged=True)
    try:record(a.run,a.out,display=a.display,case_id=a.case_id,main_scene=scene)
    finally:
        target=ROOT.parent/a.out/'consumer-binding.json'
        if target.parent.exists():
            assert not target.exists();target.write_text(json.dumps(binding,ensure_ascii=False,indent=2)+'\n')

if __name__=='__main__':main()
