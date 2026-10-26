"""Exact custom scene recordings with a complete world freeze during end hold."""
from pathlib import Path
import argparse,json,hashlib
from pcg.prototype.workshop.record import record
from pcg.prototype.workshop import record as recorder_module
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.creative_batches.enemy_world.record_v1 import RUNS
HERE=Path(__file__).parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('recipe',choices=['attack','lure']);a=p.parse_args()
 source=Path(recorder_module.__file__);before=hashlib.sha256(source.read_bytes()).hexdigest()
 out=record(RUNS[a.recipe],'pcg/results/workshop-creative-enemy-world-videos-v2/'+a.recipe,display=':106',main_scene=HERE/'main_v2.tscn')
 after=hashlib.sha256(source.read_bytes()).hexdigest()
 if before!=after:raise RuntimeError('recording_source_changed_during_run')
 (out/'source-stability.json').write_text(json.dumps(dict(shared_recorder_sha256=before,unchanged_during_native_record_and_comparison=True,display_only_change='disable all world descendants only after final recorded witness frame, complete 1sec hold'),indent=2))
 print(json.dumps(dict(recipe=a.recipe,path=str(out.relative_to(ROOT.parent)))))
