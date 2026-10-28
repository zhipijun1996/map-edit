"""Active same-world falsifiers for D04; root executes within full budget.

No phase/state/resource changes. These policies select the middle-parked world,
then deliberately try the east edge and late under-wall recoil to reach C.
Return policies are adapted to the middle park rather than blindly waiting at
an absent far platform. Use api_v3.fixture_task_outcome, NOT required final park.
"""
import copy,math
from pathlib import Path
from . import api_v3 as api
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
SOURCE_DEPENDENCIES=[Path(api.__file__)]+api.SOURCE_DEPENDENCIES

def rest():return [cmd('axis',value=0),ground(),cmd('wait',8)]
def low_to_home():
 return [cmd('axis',value=1),wait_x(520),cmd('axis',value=-1),cmd('jump'),cmd('jump_release',20),cmd('shoot',0,direction=[.7141428429,.7]),wait_x(350,-1),*rest(),cmd('axis',value=1),wait_x(300),*rest(),cmd('axis',value=0),cmd('jump'),cmd('jump_release',20),cmd('shoot',0,direction=[0,1]),cmd('wait',4),cmd('axis',value=-1),settle(80,6)]

def carrier_edge_paths(source,interface):
 # First leave B to the left, genuinely land on the already parked middle
 # carrier, then choose its east edge. No world phase or resource assignment.
 dx=interface*30;east=620+interface*45
 landed=source+[cmd('axis',value=-1),wait_x(555+dx,-1),cmd('axis',value=0),api.rules.old.on('return-deck'),cmd('wait',8),cmd('axis',value=1),wait_x(east)]
 for jump_hold,delay,dy in [(0,4,.15),(0,8,.35),(6,0,.15),(6,0,.35)]:
  launch=([cmd('jump'),cmd('jump_release',jump_hold)]if jump_hold else [cmd('wait',delay)])
  yield f'carrier-east-{east}-jump{jump_hold}-delay{delay}-dy{dy}',landed+launch+[cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy]),wait_x(1110+dx-4),*rest()]

def cases(interface=0):
 mid=api.fixtures(interface)[0];source=copy.deepcopy(mid['control_plan'][:11]);dx=interface*30;out=[]
 # Includes the critic's actual carrier-edge route and distinct direct B falls.
 approaches=list(carrier_edge_paths(source,interface))
 for shot_x,dy in [(780,.5),(800,.8660254),(820,.8660254),(800,1.)]:
  approaches.append((f'B-fall-{shot_x}-{dy}',source+[cmd('axis',value=1),wait_x(shot_x+dx),cmd('shoot',direction=[-math.sqrt(max(0,1-dy*dy)),dy]),wait_x(1110+dx-4),*rest()]))
 for approach,reach_c in approaches:
  for method in ['late-under-wall','floor-recovery']:
   if method=='late-under-wall':
    back=[cmd('axis',value=-1),wait_x(1060+dx,-1),cmd('jump'),cmd('jump_release',20),wait_x(850+dx,-1),cmd('shoot',direction=[.5,.8660254]),wait_x(470,-1),*rest()]+low_to_home()
   else:
    # Explicitly tests the safety-floor bypass. The floor is not allowed to be
    # called recovery-only if this is uniformly cheaper than the designed trip.
    back=[cmd('axis',value=-1),wait_x(570,-1),*rest(),cmd('axis',value=0),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),cmd('wait',4),cmd('axis',value=-1),wait_x(470,-1),*rest()]+low_to_home()
   c=copy.deepcopy(mid);label=f'adaptive-mid-{approach}-{method}'
   c['id']+='-counter-'+label;c['counterexample_kind']=label;c['control_plan']=reach_c+back;c['expected_reward']=12;c['route_spec']['via_ports']=['B','C'];c['max_frames']=2200
   c['counter_task_scope']='Actual A→B→C chest→A in one world, HP5 and allowed abilities. Ignore desired final park in the task comparator; compare actual shots/jumps/ticks with canonical reward-return.'
   out.append(c)
 return out

if __name__=='__main__':
 import argparse,json
 p=argparse.ArgumentParser();p.add_argument('--interface',type=int,choices=[0,1],default=0);a=p.parse_args();print(json.dumps(dict(cases=cases(a.interface)),ensure_ascii=False,indent=2))
