from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.workshop.rules import cmd
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__),HERE/'main-solve-protocol-v2.json']
DELAYS=[16,8,24,32]
def materialize(interface=0,route='air',control=0):
 c=prior.materialize(interface,route,control)
 if interface==0:
  c['spawn']=[220,420];c['entry_port']=[220,420];c['ports'][0]['position']=[220,420];c['latches'][0]['bell']=[240,380]
  c['rule_parameters']['launch']=220
  if route=='air':c['control_plan'][1]['target_x']=220
 if route=='air':c['control_plan'][3]=cmd('wait',DELAYS[control])
 c['id']=c['id'].replace('v1','v2');c['rule_parameters']['jump_after_attack']=DELAYS[control]
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','enemies','reward_sites']})
 c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
 return c
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C08 exact spaces')
 return[materialize(interface,'air',0),materialize(interface,'staged',0)]
def purpose(c,r):return prior.purpose(c,r)
def alternatives(c):return prior.alternatives(c)
