"""Parent exact counters plus ingress-specific skip-M searches, same world."""
import copy,math
from pcg.prototype.creative_batches.batch30_blockn06_repair.alternatives_v1 import alternatives as parent
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle

def alternatives(c):
 out=parent(c);entry=c['route_spec']['from_port'];target=c['route_spec']['to_port'];side=-1 if target=='B'else 1;end=c['exit_port'][0]
 for v in out:
  if entry=='D'and v['counterexample_kind'].startswith('direct-low-entry-'):
   # Parent's hardcoded west ingress must be rebound to the real east shore.
   v['control_plan'][0]=cmd('axis',value=-1);v['control_plan'][1]=wait_x(1055,-1)
  if entry=='D'and v['counterexample_kind']=='recovery-floor-no-shot':v['control_plan'][0]=cmd('axis',value=-1);v['control_plan'][1]=wait_x(900,-1)
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 incoming=1 if entry=='A'else -1;takeoff=225 if entry=='A'else 1055
 # Same-side direct bridge test:320px rise from low shore, with actual
 # ground pre-switch for the initially absent right bridge. No M waypoint.
 for hold,dy in [(20,1.0),(30,.95),(12,.85),(24,.6)]:
  prefix=[cmd('axis',value=incoming),wait_x(takeoff,incoming),cmd('axis',value=0),ground()]
  if target=='C':prefix+=[cmd('shoot',aim_cell=dict(kind='bell',id='wing-pair')),cmd('wait',12)]
  bridge_x=320 if target=='B'else 960
  plan=prefix+[cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-side*math.sqrt(max(0,1-dy*dy)),dy]),cmd('axis',value=side),wait_x(bridge_x,side),cmd('axis',value=0),ground(),cmd('wait',8)]+copy.deepcopy(c['control_plan'][18:])
  add(f'direct-low-to-bridge-skip-M-{hold}-{dy}',plan)
 # Full ordinary jump from entry to high goal, not just release-without-jump.
 for hold in [8,20,30]:
  add('ordinary-low-entry-high-'+str(hold),[cmd('axis',value=incoming),wait_x(takeoff,incoming),cmd('jump'),cmd('jump_release',hold),settle(end)])
 return out


def preliminary(c):
 wanted=['omit-entry-recoil','ordinary-M-jump-32','miss-branch-bell'if c['route_spec']['to_port']=='C'else'skip-bridge-to-rock-0.8660254','direct-low-to-bridge-skip-M-20-1.0']
 by={v['counterexample_kind']:v for v in alternatives(c)}
 return[by[k]for k in wanted]
