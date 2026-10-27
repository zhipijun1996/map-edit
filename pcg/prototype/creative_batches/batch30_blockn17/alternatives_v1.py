"""Exact frozen world, route-cost alternatives and priority geometric bypasses."""
import copy,math
from . import critical_v1 as critical
from pcg.prototype.workshop.rules import cmd,wait_x,settle,ground
def shifted_preopen(c):
 branch=copy.deepcopy(c['control_plan'][8:]);branch[2]=cmd('shoot',direction=[0,1])
 return critical.variant(c,'ground-preopen-free-vertical-at536',copy.deepcopy(c['control_plan'][:8])+[cmd('shoot',aim_cell=dict(kind='bell',id='cross-pair')),ground(),cmd('wait',12),settle(536),wait_x(542,-1),ground(),cmd('wait',12)]+branch)
def upper_to_B(c):
 from . import rules_v2 as rules
 v=rules.candidate('C',0,c['interface'],'A')
 return critical.variant(c,'paid-upper-then-over-closed-side-B',copy.deepcopy(v['control_plan'][:14])+[settle(752),wait_x(746),ground(),cmd('wait',12),cmd('jump'),cmd('jump_release',20),settle(c['exit_port'][0]),ground(),cmd('wait',20)])
def alternatives(c):
 out=[];target=c['route_spec']['to_port'];prefix=c['control_plan'][:8];shot_index=12 if target=='B'else 10
 def add(kind,plan):out.append(critical.variant(c,kind,plan))
 v=copy.deepcopy(c['control_plan']);v[shot_index]=cmd('wait');add('omit-branch-shot',v)
 for hold in [0,8,20,30]:
  if target=='B':p=copy.deepcopy(prefix)+[settle(c['exit_port'][0]),wait_x(592),cmd('jump'),cmd('jump_release',hold),ground(),cmd('wait',20)]
  else:p=copy.deepcopy(prefix)+[cmd('jump'),cmd('jump_release',hold),settle(688),ground(),cmd('wait',12)]+copy.deepcopy(c['control_plan'][14:])
  add('ordinary-M-'+str(hold),p)
 for dy in [0.,.25,.5,.8660254,1.]:
  v=copy.deepcopy(c['control_plan']);v[shot_index]=cmd('shoot',direction=[-math.sqrt(max(0,1-dy*dy)),dy]);add('free-aim-'+str(dy),v)
 for dy in [.15,.7,1.]:
  side=1 if target=='B'else -1
  add('direct-A-without-M-'+str(dy),[cmd('axis',value=1),wait_x(240),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-side*math.sqrt(max(0,1-dy*dy)),dy]),settle(c['exit_port'][0]),ground(),cmd('wait',20)])
 for x in [336,592,624]:
  side=-1 if x<560 else 1;head=copy.deepcopy(prefix)+[settle(x),wait_x(x+6 if side<0 else x-6,side),ground(),cmd('wait',12),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]if target=='C'else[-1,0])]
  tail=copy.deepcopy(c['control_plan'][11:])if target=='C'else[settle(c['exit_port'][0]),ground(),cmd('wait',20)]
  add('around-M-top-launch-'+str(x),head+tail)
 for delay in [0,12]:
  v=copy.deepcopy(c['control_plan']);v[shot_index]=cmd('shoot',delay,aim_cell=dict(kind='bell',id='cross-pair'));add('early-or-delayed-bell-'+str(delay),v)
 if target=='C':out += [critical.via_B(c),shifted_preopen(c)]
 else:out += [upper_to_B(c)]
 return out
def preliminary(c):
 by={v['counterexample_kind']:v for v in alternatives(c)}
 names=['around-M-top-launch-336','around-M-top-launch-624','ground-preopen-free-vertical-at536']if c['route_spec']['to_port']=='C'else['paid-upper-then-over-closed-side-B','early-or-delayed-bell-0']
 return[by[k]for k in names]
