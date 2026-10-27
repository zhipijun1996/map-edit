from pathlib import Path
from . import rules_v2 as prior
from pcg.prototype.workshop.rules import cmd,settle,ground
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=prior.NATIVE_SCENE
SOURCE_DEPENDENCIES=prior.SOURCE_DEPENDENCIES+[Path(prior.__file__),HERE/'main-solve-protocol-v3.json']
def materialize(interface=0,route='air',control=0):
 c=prior.materialize(interface,route,control)
 if interface==0:
  c['latches'][0]['bell']=[150,400]
  if route=='air':
   c['control_plan']=[cmd('shoot',aim_cell=dict(kind='bell',id='release')),settle(220),prior.prior.attack_wait(),cmd('wait',prior.DELAYS[control]),cmd('jump'),cmd('wait',4),settle(1000),cmd('jump_release',16),cmd('shoot',aim_cell=dict(kind='enemy',id='borrowed-charger')),cmd('shoot',18,aim_cell=dict(kind='bell',id='release')),settle(c['exit_port'][0]),ground(),cmd('wait',10)]
   c['rule_parameters'].update(jump_hold=20,vertical_before_lateral=4)
 c['id']=c['id'].replace('v2','v3');c['generation_rule'].update(version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['layout_uid']=digest({k:c.get(k,[])for k in ['platforms','ports','latches','enemies','reward_sites']})
 c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid'];return c
def layouts(recipe,interface):
 if recipe not in RECIPES or interface not in [0,1]:raise ValueError('outside C08 exact spaces')
 return[materialize(interface,'air',0),materialize(interface,'staged',0)]
def purpose(c,r):return prior.purpose(c,r)
def alternatives(c):return prior.alternatives(c)
