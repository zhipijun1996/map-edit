"""Final C04 source binding with deterministic real gate support names."""
from pathlib import Path
from . import rules_v2 as prior
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=HERE/'runner_v2.gd'
NATIVE_SCENE=HERE/'main_v2.tscn'
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__)]+[HERE/n for n in ['protocol-v3.json','stable_support_names_v1.gd','runner_v2.gd','main_v2.gd','main_v2.tscn']]
def materialize(interface=0,control=0):
 c=prior.materialize(interface,control);c['id']=c['id'].replace('v2','v3');c['native_scene']='res://prototype/creative_batches/batch30_c04/main_v2.tscn';c['generation_rule'].update(version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])));return c
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C04 exact interfaces')
 return[materialize(interface,0)]
def purpose(c,r):return prior.purpose(c,r)
def alternatives(c):return prior.alternatives(c)
