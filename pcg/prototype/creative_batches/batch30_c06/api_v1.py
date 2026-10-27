"""Frozen C06 registry over the two actual falling-fork worlds."""
from pathlib import Path
from . import rules_v2 as rules
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'recovery_v1.py']
def layouts(recipe,interface):
 cs=rules.layouts(recipe,interface)
 for c in cs:
  c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
  c['map_specification']['objective']['junction_role']='fork'
  c['map_specification']['objective']['junction_pattern']='falling_layer_choice'
 return cs
def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):return rules.alternatives(c)
