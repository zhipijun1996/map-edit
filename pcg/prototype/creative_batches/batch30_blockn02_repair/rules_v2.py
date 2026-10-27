"""Same world, real horizontal brake input while P2 actively catches up."""
from pathlib import Path
from . import rules_v1 as old
from pcg.prototype.workshop.rules import cmd
HERE=Path(__file__).parent
RECIPES=old.RECIPES;RUNNER_SCRIPT=old.RUNNER_SCRIPT;NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json',HERE/'probe_v2.py']

def candidate(interface=0,control=0,route='high'):
 c=old.candidate(interface,control,route)
 if route=='high':
  i=next(i for i,q in enumerate(c['control_plan'])if q.get('aim_cell',{}).get('id')=='intercept-start')
  c['control_plan'].insert(i+1,cmd('axis',value=0))
 c['id']=c['id'].replace('receiver-v1','receiver-v2');c['rule_parameters']['first_high_recoil_brake_axis']=0
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 return c

purpose=old.purpose
