"""Bounded side-pocket control repair; v3 world/collisions are immutable."""
import copy,math
from pathlib import Path
from . import rules_v3 as prior
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
HERE=Path(__file__).parent
RECIPES=prior.RECIPES
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
NATIVE_SCENE=HERE/'main_v1.tscn'
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v4.json',HERE.parents[2]/'creative-production/batch30/protocol-v9.json']
purpose=prior.purpose
def candidate(control=0,route='staged'):
 c=prior.candidate(0,1 if route=='air' else (3 if control==0 else 1),route)
 c['id']=f'b30-c03-v4-i0-{route}-r{control}'
 if route=='staged':
  if control==1:c['control_plan'][4]['direction']=[-.95,math.sqrt(1-.95*.95)]
  elif control==2:c['control_plan'][10:10]=[cmd('shoot',aim_cell=dict(kind='bell',id='window-path-pair'))]
  elif control==3:c['control_plan'][4]['direction']=[-.9,math.sqrt(1-.9*.9)]
 c['rule_parameters'].update(control_repair=control,geometry_rule_version=3)
 c['generation_rule']=dict(id='batch30/C03',version=4,geometry_version=3,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 c['native_scene']='res://prototype/creative_batches/batch30_c03/main_v1.tscn'
 return c

def dead_fixture(control=0):
 c=candidate(control,'staged');base=prior.dead_fixture(0,1);tail=prior.candidate(0,1,'staged')['control_plan']
 c['id']+='-actual-death-fixture';c['control_plan']=base['control_plan'][:-len(tail)]+c['control_plan'];c['max_frames']=2200;c['validation_fixture']=base['validation_fixture'];return c

def closed_window_fixture(control=0,after_exchange=False):
 c=candidate(0,'air');source=copy.deepcopy(c['control_plan']);c['id']+='-closed-window-'+('after-return'if after_exchange else'initial')
 attack=[cmd('axis',value=0),cmd('jump'),cmd('axis',6,value=1),cmd('jump_release',10),cmd('shoot',6,aim_cell=dict(kind='enemy',id='window-sentry')),cmd('wait',20),settle(80,6)]
 prefix=[]
 if after_exchange:prefix=source[:-1]+[wait_x(450),*prior.prior.rest(),cmd('axis',value=-1),wait_x(80,-1),*prior.prior.rest()]
 c['control_plan']=prefix+attack;c['goal']=[55,416,50,8];c['max_frames']=1600;c['validation_fixture']=dict(kind='closed_window_projectile_rejection_after_actual_return'if after_exchange else'closed_window_projectile_rejection',no_module_enrollment=True);return c
