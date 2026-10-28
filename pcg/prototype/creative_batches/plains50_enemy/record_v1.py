"""Unmodified strict recorder and existing native Cell consumer."""
from pathlib import Path
import argparse,json
from .rules_v2 import RECIPES
from pcg.prototype.workshop.record import record
from pcg.prototype.workshop.engine import ROOT
HERE=Path(__file__).parent
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('recipe',choices=RECIPES);p.add_argument('--display',default=':112');a=p.parse_args()
 scene=HERE.parent/'enemy_world/main_v2.tscn'if a.recipe in ['attack-relay','live-enemy-sensor']else None
 out=record('workshop-plains50-enemy-r2-'+a.recipe+'/round-00','pcg/results/workshop-plains50-enemy-media-v1/'+a.recipe,display=a.display,main_scene=scene)
 print(json.dumps(dict(recipe=a.recipe,path=str(out.relative_to(ROOT.parent)))))
