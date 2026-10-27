"""Last rule: obey original access-side eligibility and shield shore prefire."""
import copy
from pathlib import Path
from . import rules_v1 as parent
from pcg.prototype.workshop.rules import cmd,wait_x,ground
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=parent.RECIPES;RUNNER_SCRIPT=parent.RUNNER_SCRIPT;NATIVE_SCENE=parent.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(parent.__file__),*parent.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
def access_position(plan):
 p=[]
 for q in copy.deepcopy(plan):
  if q.get('op')=='shoot'and q.get('aim_cell',{}).get('receiver')=='access':
   p +=[cmd('axis',value=1),wait_x(600),cmd('axis',value=0),ground(),cmd('wait',8)]
  p.append(q)
 return p
def candidate(control=0):
 c=parent.candidate(control);c['id']=c['id'].replace('n19-v1','n19-v2')
 c['platforms'].append([320,200,24,112]);c['control_plan']=access_position(c['control_plan'])
 c['rule_parameters'].update(M_shoot_position=600,prefire_baffle=[320,200,24,112],head_clearance_at_floor352=4,rule=2)
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
 return c
purpose=parent.purpose
outcome=parent.outcome
