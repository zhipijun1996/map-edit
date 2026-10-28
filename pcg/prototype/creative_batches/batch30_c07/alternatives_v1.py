import copy
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def alternatives(c):
 out=[];source=c['control_plan'];sign=1 if c['interface']==0 else -1;point=c['exit_port'][0];edge=220 if sign==1 else 340
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for i in [2,12]:
  p=copy.deepcopy(source);p[i]=dict(op='wait',trigger=p[i]['trigger']);add(f'omit-shot-{i}',p)
 for hold in [8,20,32]:add(f'ordinary-jump-{hold}',[cmd('axis',value=sign),wait_x(edge,sign),cmd('jump'),cmd('jump_release',hold),settle(point)])
 for hold in [8,20,32]:add(f'ground-preopen-{hold}',[cmd('shoot',aim_cell=dict(kind='bell',id='brake-pair')),cmd('wait',25),cmd('axis',value=sign),wait_x(edge,sign),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-.8*sign,.6]),settle(point)])
 for hold in [8,20,32]:add(f'air-preopen-then-land-{hold}',[cmd('axis',value=sign),wait_x(edge,sign),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,aim_cell=dict(kind='bell',id='brake-pair')),cmd('axis',value=0,after=6),cmd('wait',100),ground(),cmd('axis',value=sign),wait_x(edge,sign),cmd('jump'),cmd('jump_release',8),cmd('shoot',6,direction=[-.8*sign,.6]),settle(point)])
 for axis in [0,sign]:
  for delay in [0,6,12]:
   p=copy.deepcopy(source);p[3]=cmd('axis',value=axis,after=delay);add(f'no-active-wall-drive-axis{axis}-after{delay}',p)
 add('direct-fall-no-pocket-no-shot',[cmd('axis',value=sign),settle(point,30)])
 assert len(out)==18
 return out
