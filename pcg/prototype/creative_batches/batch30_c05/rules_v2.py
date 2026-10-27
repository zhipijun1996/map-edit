"""C05 proper external near port and a body-feasible parked-deck boarding jump."""
from pathlib import Path
from . import rules_v1 as old
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=old.RECIPES
RUNNER_SCRIPT=old.RUNNER_SCRIPT
NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
def candidate(interface=0,control=0,route='near'):
 c=old.candidate(interface,control,route);c['id']=c['id'].replace('v1','v2');c['control_plan'][1]=wait_x(205)
 c['ports'][1].update(position=[180,382],support_index=3)
 c['reward_sites'][0].update(position=[180,382],region=[150,377,60,10])
 if route=='near':
  c['exit_port']=[180,382];c['goal']=[155,378,50,8]
  c['control_plan']=c['control_plan'][:11]+[wait_x(c['rule_parameters']['departure_actor_x']),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),wait_x(450,-1),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=-1),wait_x(405,-1),cmd('jump'),cmd('jump_release',8),settle(180,6)]
 c['rule_parameters'].update(boarding_takeoff_x=205,near_landing_bank_is_internal=True,port_B='upper-west original roof, outside full carrier envelope')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites']})
 c['generation_rule']=dict(id='batch30/C05',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 return c
def purpose(c,r):
 if not r.get('frames'):return dict(ok=False,reasons=[r.get('reason','no_actual_frames')],causal=dict(neutral_carried_frames=0,neutral_carried_dx=0),behavior={})
 return old.purpose(c,r)
