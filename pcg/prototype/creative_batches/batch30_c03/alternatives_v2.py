"""Exact-world low-cost searches, including held jumps and finite overtop tradeoff."""
import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,settle
def alternatives(c):
 out=[];source=c['control_plan'];shot_indices=[i for i,q in enumerate(source)if q['op']=='shoot']
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for i in shot_indices:
  p=copy.deepcopy(source);p[i]=dict(op='wait',trigger=p[i]['trigger']);add('omit-shot-'+str(i),p)
 for hold in [8,12,16,20,24,28,36]:
  for dy in [.6,.8660254,1.]:
   for delay in [0,10]:
    add(f'initial-open-path-one-shot-{hold}-{dy}-{delay}',[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('jump_release',hold),cmd('shoot',delay,direction=[-math.sqrt(max(0,1-dy*dy)),dy]),settle(c['exit_port'][0])])
 for shot in [6,12,18,24]:
  for hold in [8,20,36]:add(f'held-jump-one-shot-{shot}-{hold}',[cmd('axis',value=1),wait_x(205),cmd('jump'),cmd('shoot',shot,direction=[0,1]),cmd('jump_release',hold),settle(c['exit_port'][0])])
 if c['route_spec']['id']=='air':
  for delay in [18,24,35]:
   p=copy.deepcopy(source);p[7]=cmd('shoot',delay,aim_cell=dict(kind='enemy',id='window-sentry'));p[8:8]=[cmd('shoot',35,direction=[0,1])];add('borrow-twice-overtop-different-world-'+str(delay),p)
 else:
  for hold in [12,20,28]:
   p=copy.deepcopy(source);i=next(i for i,q in enumerate(p)if q['op']=='jump_release');p[i]['trigger']['after']=hold;p[shot_indices[0]]=dict(op='wait',trigger=p[shot_indices[0]]['trigger']);add('ordinary-first-stage-allowed-'+str(hold),p)
 return out
