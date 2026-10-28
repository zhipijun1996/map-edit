import copy
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def alternatives(c):
 out=[];p=c['control_plan'];shots=[i for i,v in enumerate(p)if v['op']=='shoot'];jumps=[i for i,v in enumerate(p)if v['op']=='jump']
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 for label,j in zip(['omit-near-shot','omit-far-shot'],shots):
  q=copy.deepcopy(p);q[j]=dict(op='wait',trigger=q[j]['trigger']);add(label,q)
 for hold in [8,20,32]:add('ordinary-M-jump-'+str(hold),copy.deepcopy(p[:jumps[-1]+1])+[cmd('jump_release',hold),settle(1256,0)])
 for dy in [-14,0,14]:
  q=copy.deepcopy(p);q[shots[0]]=cmd('shoot',aim_target=[800,672+dy]);add('aim-direct-far-first-y'+str(dy),q)
 for x in [640,740]:
  add('ground-double-preopen-x'+str(x),[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='far')),cmd('wait',20),cmd('shoot',aim_cell=dict(kind='bell',id='far')),cmd('wait',20)]+copy.deepcopy(p))
 for dy in [-14,0,14]:
  prefix=copy.deepcopy(p[:8]);add('roof-prefire-far-y'+str(dy),prefix+[cmd('shoot',aim_target=[800,672+dy]),cmd('wait',20)]+copy.deepcopy(p[8:]))
 q=copy.deepcopy(p);q.insert(jumps[-1],cmd('wait',120));add('late-M-receiver-reset',q)
 q=copy.deepcopy(p);q.insert(jumps[-1],cmd('shoot',aim_cell=dict(kind='bell',id='far')));q.insert(jumps[-1]+1,cmd('wait',20));add('ground-M-paid-preopen',q)
 for offset in [0,4]:
  prefix=copy.deepcopy(p[:shots[0]]);add('enter-body-into-receiver-alcove-'+str(offset),prefix+[cmd('axis',value=-1),wait_x(810,-1),cmd('axis',value=0),cmd('shoot',offset,aim_cell=dict(kind='bell',id='far')),cmd('axis',value=1)]+copy.deepcopy(p[shots[0]:]))
 add('over-first-gate-upshot',copy.deepcopy(p[:8])+[cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),settle(1256,0)])
 add('walk-fall-below-gates',[cmd('axis',value=1),settle(1256,0)])
 q=copy.deepcopy(p);q[shots[1]]=cmd('shoot',4,direction=[-1,0]);add('miss-far-after-near-released',q)
 assert len(out)==20,len(out)
 return out
