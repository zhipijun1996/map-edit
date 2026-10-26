"""Manual native consumer of the exact eight enrolled cases."""
from pathlib import Path
import argparse,json,subprocess
from .rules_v2 import RECIPES
from pcg.prototype.workshop.engine import ROOT
from pcg.prototype.factory.core.engine import ENGINE
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--recipe',choices=RECIPES,default='attack-relay');p.add_argument('--interface',type=int,choices=[0,1],default=0);p.add_argument('--print-command',action='store_true');a=p.parse_args()
 cases=ROOT/'results'/('workshop-plains50-enemy-r2-'+a.recipe)/'round-00/review_cases.json';payload=json.loads(cases.read_text());assert len(payload['cases'])==2
 scene=Path(__file__).parent.parent/'enemy_world/main_v2.tscn'
 command=[str(ENGINE),'--path',str(ROOT/'prototype/godot'),str(scene.resolve()),'--','--cases-json',str(cases),'--case',str(a.interface)]
 if a.print_command:print(json.dumps(command,ensure_ascii=False))
 else:subprocess.run(command,check=True)
