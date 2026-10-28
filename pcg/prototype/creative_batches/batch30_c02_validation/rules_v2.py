"""Return under the original access bell before the anti-pinch-safe reset shot."""
from pathlib import Path
from . import rules_v1 as previous
from pcg.prototype.workshop.rules import settle
HERE=Path(__file__).parent
RUNNER_SCRIPT=previous.RUNNER_SCRIPT
NATIVE_SCENE=previous.NATIVE_SCENE
SOURCE_DEPENDENCIES=previous.SOURCE_DEPENDENCIES+[Path(previous.__file__),HERE/'protocol-v2.json']
def fixture(interface=1,control=0):
 if interface!=1:raise ValueError('v2 repair is only the unqualified interface1')
 c=previous.fixture(interface,control);c['id']=c['id'].replace('recovery-v1','recovery-v2')
 ix=next(i for i,q in enumerate(c['control_plan'])if q.get('aim_cell',{}).get('receiver')=='access')
 c['control_plan'][ix:ix]=[settle(430),previous.support(c,3,430)]
 c['validation_fixture']['access_reset_shot_x']=430
 return c
def purpose(c,r):return previous.purpose(c,r)
