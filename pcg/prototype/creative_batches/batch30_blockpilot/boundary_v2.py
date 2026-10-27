"""Controller-only revision of the exact two-source boundary specimen."""
from pathlib import Path
from . import boundary_v1 as previous
from pcg.prototype.workshop.rules import cmd,settle,wait_x
from pcg.prototype.factory.core.quality import digest

HERE=Path(__file__).parent
RUNNER_SCRIPT=previous.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(previous.__file__),*previous.SOURCE_DEPENDENCIES,HERE/'boundary-protocol-v2.json']
purpose=previous.purpose

def case():
    c=previous.case()
    source=c['boundary_fixture']['source_left_case']
    c['control_plan']=previous.prefixed(source,'left')['control_plan']+[
        settle(874,0),wait_x(870),cmd('wait',20),
        settle(922,0),wait_x(918),cmd('wait',20),
        settle(838,0),wait_x(842,-1),cmd('wait',20)]
    c['id']='b30-block-boundary-v2-c0'
    c['boundary_fixture']['fixture_version']='sha256:'+digest(dict(
        platforms=c['platforms'],latches=c['latches'],control_plan=c['control_plan'],
        left_input=c['boundary_fixture']['source_input_sha256']))
    return c
