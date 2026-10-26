"""Control-only recovery repair; same original bodies and frozen core world."""
from pathlib import Path
from . import recovery_v1 as prior
from . import rules_v2 as core
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
HERE=Path(__file__).parent
rules=core
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v3.json']
def materialize(interface=0,control=0,main_control=0):
 c=prior.materialize(interface,control,main_control)
 prefix=c['control_plan'][:11]
 back=wait_x([-335,-330][control],-1);back['trigger']['timeout']=480
 steps=[cmd('axis',value=-1),back,cmd('axis',value=0),cmd('jump'),cmd('wait',6),settle(-430),cmd('jump_release',14),ground(),cmd('wait',16)]
 for x in [-340,-250,-160]:
  steps += [settle(x),cmd('jump'),cmd('jump_release',20),ground(),cmd('wait',16)]
 steps += [settle(80),wait_x(76),ground(),cmd('wait',12),settle(1000)]
 c['control_plan']=prefix+steps+core.materialize(interface,main_control)['control_plan']
 c['id']=c['id'].replace('recovery-r','recovery2-r');c['rule_parameters']['first_stair_takeoff']=[-335,-330][control]
 return c
def purpose(c,r):return prior.purpose(c,r)
