"""Frozen production registration for C01; probes do not confer admission."""
import json
from pathlib import Path
from . import rules_v3 as rules
from .alternatives_v2 import alternatives
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=HERE/'runner_v1.gd'
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,*[HERE/n for n in ['control-selection-v1.json','alternatives_v2.py','runner_v1.gd','main_v1.gd','main_v1.tscn']]]
CONTROL={int(k):v for k,v in json.loads((HERE/'control-selection-v1.json').read_text())['controls'].items()}
purpose=rules.purpose
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in CONTROL:raise ValueError('outside registered C01 family/space demands')
 c=rules.candidate(interface,CONTROL[interface]);c['native_scene']=str(NATIVE_SCENE)
 c['map_specification']=rules.specification(interface,c)
 c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]))
 return [c]
