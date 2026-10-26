"""Original production loop; four existing causal families, eight demand versions."""
from pathlib import Path
import argparse,json
from .rules_v2 import compiler,purpose,alternatives,sources,runner,exporter,RECIPES
from pcg.prototype.workshop.production_loop import run
from pcg.prototype.workshop.engine import ROOT
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--recipe',choices=RECIPES);p.add_argument('--name-prefix',default='workshop-plains50-enemy-r2');a=p.parse_args()
 for recipe in [a.recipe]if a.recipe else RECIPES:
  run(a.name_prefix+'-'+recipe,requests=[dict(recipe=recipe,interfaces=[0,1])],cycles=1,library_root=ROOT/'map_directed/library',compiler=compiler,checker=purpose,counter_builder=alternatives,source_file=Path(__file__).with_name('rules_v2.py'),extra_sources=sources()+[Path(__file__)],runner_script=runner(recipe),export_script=exporter(recipe))
