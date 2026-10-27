"""Two explicit terminal controls over the immutable active-transfer world."""
from pathlib import Path
from pcg.prototype.creative_batches.batch30_blockn02_repair import rules_v2 as old
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
HERE=Path(__file__).parent
RECIPES=old.RECIPES;RUNNER_SCRIPT=old.RUNNER_SCRIPT
NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v1.json',HERE.parent/'batch30_blockn02_repair/probe-receipt-v1.json']

def candidate(interface=0,terminal=0,route='high'):
 if terminal not in [0,1]:raise ValueError('outside_registered_two_terminal_controls')
 c=old.candidate(interface,0,route)
 if route=='high':
  shots=[i for i,q in enumerate(c['control_plan'])if q['op']=='shoot'];j=shots[-1]
  if terminal==0:c['control_plan'][j]['direction']=[-.5,.8660254037844386]
  else:
   c['control_plan'][-1]=settle(1232)
   c['control_plan'] += [ground(),cmd('wait',8),cmd('axis',value=1),wait_x(1252),settle(1256)]
   # Persistent settle remains originalcontroller behavior. Replacing its
   # target (rather than merelysettingaxis) makes the finalwalk physicallyreal.
   c['control_plan'][-3]=settle(1256)
 c['id']=c['id'].replace('b30-blockn02-receiver-v2',f'b30-blockn02-terminal-v1-t{terminal}')
 target=[1256,206 if route=='high' else 590];c['goal']=[1249,target[1]-4,14,8]
 c['rule_parameters'].update(terminal_control=terminal,strict_dock_goal=c['goal'],old_receiver_cycle_status='needs_design7cases',outer_cycle='root_explicit_terminal_control_repair')
 c['generation_rule']=dict(id='batch30/blockN02-terminal-control',version=1,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'],physics_world_unchanged=True,prior_goal_was_already_strict=True)
 return c

purpose=old.purpose
