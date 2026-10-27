"""Final bounded control revision; original steering API is used correctly."""
import copy,json
from pathlib import Path
from . import rules_v1 as prior
from pcg.prototype.workshop.rules import cmd,wait_x,ground
HERE=Path(__file__).parent
PROTOCOL=json.loads((HERE/'protocol-v2.json').read_text())
RUNNER_SCRIPT=prior.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(prior.__file__),*prior.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
purpose=prior.purpose
def fixture(interface=0,control=0):
 c=prior.fixture(interface,0);core=prior.core.layouts(prior.core.RECIPES[0],interface)[0];option=PROTOCOL['controls'][control];x=option['floor_takeoff_x']
 p=copy.deepcopy(core['control_plan'][:9])+[cmd('shoot',direction=[0,1]),cmd('axis',value=1),wait_x(850),cmd('axis',value=0),ground(),cmd('wait',6)]
 p += [cmd('axis',value=-1),wait_x(x,-1),cmd('axis',value=0),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',option['jump_release_delay']),cmd('shoot',direction=[0,1]),cmd('wait',option['turn_left_after_shot']),cmd('axis',value=-1),wait_x(380,-1),cmd('axis',value=0),ground(),cmd('wait',6)]
 p += [cmd('axis',value=-1),wait_x(-100,-1),cmd('axis',value=0),ground(),cmd('wait',10)]+copy.deepcopy(core['control_plan'])
 c['control_plan']=p;c['id']=f'b30-block-d05-independent-recovery-v2-i{interface}-c{control}'
 c['validation_fixture'].update(control=control,floor_takeoff_x=x,jump_release_delay=option['jump_release_delay'],turn_left_after_shot=option['turn_left_after_shot'],intermediate_settle_removed=True)
 return c
