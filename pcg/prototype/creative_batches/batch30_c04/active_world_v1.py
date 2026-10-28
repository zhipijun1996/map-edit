"""Same final rules, observed before original world freeze in both consumers."""
from pathlib import Path
from . import rules_v3 as prior
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=HERE/'runner_v3.gd'
NATIVE_SCENE=HERE/'main_v3.tscn'
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__)]+[HERE/n for n in ['observer-sampling-protocol-v1.json','runner_v3.gd','main_v3.gd','main_v3.tscn']]
def materialize(interface=0,control=0):
 c=prior.materialize(interface,control);c['id']+='-active1';c['native_scene']='res://prototype/creative_batches/batch30_c04/main_v3.tscn';c['generation_rule']['observer_adapter']='batch30_c04/active_world_v1';return c
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C04 exact demands')
 return[materialize(interface,0)]
def purpose(c,r):return prior.purpose(c,r)
def alternatives(c):return prior.alternatives(c)
