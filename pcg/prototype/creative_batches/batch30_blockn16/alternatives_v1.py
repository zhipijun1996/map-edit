"""Exact-world goals, not mandatory collision words."""
import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def alternatives(c):
 out=[]
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 original=c['control_plan'];prefix=original[:5]
 v=copy.deepcopy(original);v[7]=cmd('wait');add('omit-shot',v)
 for hold in [0,8,20,30]:
  add('ordinary-jump-'+str(hold),copy.deepcopy(prefix)+[cmd('jump'),cmd('jump_release',hold),settle(1000),ground(),cmd('wait',20)])
 for launch in [580,564,548,532,500,468]:
  v=copy.deepcopy(original);v[1]=wait_x(launch);v[6]=cmd('jump_release',20);add('detached-'+str(launch),v)
 for launch in [580,592]:
  v=copy.deepcopy(prefix);v[1]=wait_x(launch);add('ground-preopen-vertical-'+str(launch),v+[cmd('shoot',aim_cell=dict(kind='bell',id='wall-bell')),ground(),cmd('wait',12),cmd('jump'),cmd('jump_release',24),cmd('shoot',direction=[0,1]),settle(1000),ground(),cmd('wait',20)])
 for i,d in enumerate([[-1,0],[0,1],[-.85,math.sqrt(1-.85**2)]]):
  v=copy.deepcopy(original);v[7]=cmd('shoot',direction=d);add('miss-bell-'+str(i),v)
 v=copy.deepcopy(original);v[7]=cmd('shoot',direction=[0,1]);v[8:]=[settle(830),ground(),cmd('wait',12),cmd('jump'),cmd('jump_release',24),cmd('shoot',direction=[0,1]),settle(1000),ground(),cmd('wait',20)];add('over-high-door-without-hit',v)
 add('walk-no-jump-shot',[cmd('axis',value=1),settle(1000),ground(),cmd('wait',20)])
 for delay in [0,12]:
  v=copy.deepcopy(original);v[6]=cmd('jump_release',4);v[7]=cmd('shoot',delay,aim_cell=dict(kind='bell',id='wall-bell'));add('early-shot-'+str(delay),v)
 return out
def preliminary(c):
 keys=['omit-shot','ordinary-jump-30','detached-532','detached-468','ground-preopen-vertical-592','miss-bell-1','over-high-door-without-hit']
 by={v['counterexample_kind']:v for v in alternatives(c)};return[by[k]for k in keys]
