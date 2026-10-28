"""Frozen C02 registry: two measured spaces, original-air-shot pair order."""
import copy,math
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
HERE=Path(__file__).parent
RECIPES=rules.RECIPES
RUNNER_SCRIPT=rules.RUNNER_SCRIPT
NATIVE_SCENE=rules.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'protocol-v3.json']
CONTROL={0:0,1:0}
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in CONTROL:raise ValueError('outside frozen C02 space demands')
 c=rules.materialize(interface,CONTROL[interface]);c['generation_rule']['registration_source']=str(Path(__file__).relative_to(HERE.parents[3]));return[c]
def purpose(c,r):return rules.purpose(c,r)
def alternatives(c):
 out=[v for v in rules.alternatives(c)if not v['counterexample_kind'].startswith('ground-middle-open-and-climb-')]
 far=c['latches'][0]['paired_gate'][0];target=c['exit_port'][0]
 for launch in [400,far-100,far-40]:
  for dy in [.75,.95,1.]:
   label=f'reachable-ground-middle-open-and-climb-{launch}-{dy}'
   v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label
   v['control_plan']=[cmd('axis',value=1),wait_x(launch),cmd('axis',value=0),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='airlock-pair',receiver='access')),cmd('wait',24),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',6,direction=[-math.sqrt(max(0,1-dy*dy)),dy]),settle(target,6)]
   out.append(v)
 return out
