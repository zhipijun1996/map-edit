"""Active pre-switch falsifiers continue from B if they really reach it."""
import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,settle
def alternatives(c):
 out=[];source=c['control_plan'];shots=[i for i,q in enumerate(source)if q['op']=='shoot']
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for i in shots:
  p=copy.deepcopy(source);p[i]=dict(op='wait',trigger=p[i]['trigger']);add('omit-shot-'+str(i),p)
 for hold in [6,12,20,28]:
  p=[cmd('axis',value=1),wait_x(c['rule_parameters']['launch_x']),cmd('jump'),cmd('jump_release',hold),settle(c['exit_port'][0])];add('ordinary-long-jump-'+str(hold),p)
 for hold in [6,16,28]:
  for delay in [6,18,30]:
   for dy in [.15,.6,.8660254]:
    p=[cmd('shoot',aim_cell=dict(kind='bell',id='bridge-pair')),cmd('wait',35),cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',hold),cmd('shoot',delay,direction=[-math.sqrt(1-dy*dy),dy])]+copy.deepcopy(source[shots[0]+1:])
    add(f'shore-flip-active-{hold}-{delay}-{dy}',p)
 p=copy.deepcopy(source);p[shots[0]+1:shots[0]+1]=[cmd('shoot',18,direction=[-.8,.6])];add('extra-air-shot-skip-landing',p)
 for hold in [6,12,20,28]:
  p=copy.deepcopy(source);p[shots[1]-1]['trigger']['after']=hold;p[shots[1]]=dict(op='wait',trigger=p[shots[1]]['trigger']);add('onward-ordinary-hop-allowed-'+str(hold),p)
 return out
