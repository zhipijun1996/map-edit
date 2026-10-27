import copy,math
from . import rules_v2 as rules
from .core_v2 import candidate as core
from .cheap_v2 import candidate as cheap
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def alternatives(c):
 if c['interface']!=0:raise ValueError('onlyactualEastcountersetcurrentlyregistered')
 out=[];p=c['control_plan'];shots=[i for i,q in enumerate(p)if q['op']=='shoot'];park=shots[1];j=next(i for i,q in enumerate(p)if q['op']=='jump')
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 for kind,s in [('omit-start',shots[0]),('omit-parking',park),('omit-exit-shot',shots[2])]:
  q=copy.deepcopy(p);q[s]=dict(op='wait',trigger=q[s]['trigger']);add(kind,q)
 for kind in ['no-stop-immediate','no-stop-wait8']:add(kind,cheap(kind)['control_plan'])
 for delay in [15,60,100]:
  q=[cmd('axis',value=1),wait_x(130),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='deck-control')),cmd('wait',delay),cmd('axis',value=1),wait_x(130),cmd('axis',value=0),ground(),cmd('shoot',aim_target=[1320,538]),cmd('axis',value=1),wait_x(1260),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.5,math.sqrt(.75)]),settle(1640,0)]
  add('safe-shore-prestop-'+str(delay),q)
 for hold in [0,8,20,32]:add('ordinary-exit-'+str(hold),copy.deepcopy(p[:j+1])+[cmd('jump_release',hold),settle(1640,0)])
 rear=core(0)['control_plan'][:-1]+copy.deepcopy(p[park+1:]);add('rear-no-forward-budget',rear)
 for x in [1000,1050,1100]:
  q=copy.deepcopy(p);wait=q[park-1];assert wait['op']=='wait';wait['trigger']['dynamic']['value']=x;add('earlier-parking-'+str(x),q)
 add('ground-exit-preparation',copy.deepcopy(p[:j])+[cmd('shoot',direction=[-.5,math.sqrt(.75)]),cmd('wait',8)]+copy.deepcopy(p[j:]))
 add('bottom-approach',[cmd('axis',value=1),wait_x(500),cmd('axis',value=0),ground(),cmd('axis',value=1),wait_x(1320),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.5,math.sqrt(.75)]),settle(1640,0)])
 for x in [1200,1260]:
  q=cheap('no-stop-immediate')['control_plan'];jump=next(i for i,v in enumerate(q)if v['op']=='jump');q[jump-1]=wait_x(x);add('no-stop-exit-at-'+str(x),q)
 assert len(out)==20,len(out)
 return out
