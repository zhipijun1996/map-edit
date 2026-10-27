import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,settle
def alternatives(c):
 out=[];source=c['control_plan'];indices=[i for i,q in enumerate(source)if q['op']=='shoot']
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for i in indices:
  p=copy.deepcopy(source);p[i]=dict(op='wait',trigger=p[i]['trigger']);add('omit-shot-'+str(i),p)
 for hold in [12,20,28]:
  for dy in [.6,.8660254,1.]:
   for delay in [0,10]:
    p=[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',hold),cmd('shoot',delay,direction=[-math.sqrt(max(0,1-dy*dy)),dy]),settle(c['exit_port'][0])]
    add(f'initial-open-path-single-air-shot-{hold}-{dy}-{delay}',p)
 add('ordinary-jump-no-shot',[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',32),settle(c['exit_port'][0])])
 return out
