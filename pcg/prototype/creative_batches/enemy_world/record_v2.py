"""Scene-aware wrapper for the parent's strict native recorder API."""
from pathlib import Path
import argparse,json
from pcg.prototype.workshop.record import record
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.creative_batches.enemy_world.record_v1 import RUNS
HERE=Path(__file__).parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('recipe',choices=RUNS);p.add_argument('--display',default=':106');a=p.parse_args()
 out=record(RUNS[a.recipe],'pcg/results/workshop-creative-enemy-world-videos-v1/'+a.recipe,display=a.display,main_scene=HERE/'main_v1.tscn'if a.recipe in ['attack','lure']else None)
 print(json.dumps(dict(recipe=a.recipe,path=str(out.relative_to(ROOT.parent))),ensure_ascii=False))
