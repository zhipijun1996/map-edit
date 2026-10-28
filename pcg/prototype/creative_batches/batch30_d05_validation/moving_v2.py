"""Approach the original shore before a real dock-pausing recovery shot."""
from pathlib import Path
from . import moving_v1 as previous
from pcg.prototype.workshop.rules import cmd,wait_x,ground
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=previous.SOURCE_DEPENDENCIES+[Path(previous.__file__),HERE/'protocol-v4.json']
RUNNER_SCRIPT=previous.RUNNER_SCRIPT
CONTROLS=[(185,0),(205,0),(220,0),(205,1)]
def fixture(interface=0,control=0):
 shore,window=CONTROLS[control];c=previous.fixture(interface,window);c['id']=f'b30-d05-moving-recovery-v2-i{interface}-c{control}'
 ix=next(i for i,q in enumerate(c['control_plan'])if q.get('trigger',{}).get('carrier_observation',{}).get('running')is True)
 c['control_plan'][ix:ix]=[cmd('axis',value=1),wait_x(shore),cmd('axis',value=0),ground(),cmd('wait',6)]
 c['validation_fixture'].update(control=control,shore_pause_shot_x=shore)
 return c
def purpose(c,r):return previous.purpose(c,r)
