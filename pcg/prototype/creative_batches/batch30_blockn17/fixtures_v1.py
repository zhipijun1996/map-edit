import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,settle,ground
def floor_retry(c):
 v=copy.deepcopy(c);v['id']+='-same-world-original-floor-step-M-retry';v['probe_kind']='specific_failure_recovery_fixture';v['max_frames']=2000
 v['control_plan']=copy.deepcopy(c['control_plan'][:8])+[cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-1,0]),settle(688),ground(),cmd('wait',20),settle(520),wait_x(526,-1),ground(),cmd('wait',12),settle(400),cmd('jump'),cmd('jump_release',20),ground(),cmd('wait',12),settle(304),wait_x(310,-1),ground(),cmd('wait',12),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.35,math.sqrt(1-.35**2)]),settle(560),wait_x(553),ground(),cmd('wait',20)]+copy.deepcopy(c['control_plan'][8:])
 return v
