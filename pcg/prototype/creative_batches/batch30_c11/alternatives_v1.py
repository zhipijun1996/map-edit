import copy,math
from pcg.prototype.creative_batches.descending_carrier.counters_v1 import alternatives as old
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def alternatives(c):
 out=[]
 def add(label,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+label;v['counterexample_kind']=label;v['control_plan']=plan;out.append(v)
 for original in old():add('regression-'+original['counterexample_kind'],copy.deepcopy(original['control_plan']))
 for hold in[8,20]:
  for dy in[.6,.8660254037844386,1.]:
   plan=[cmd('axis',value=1),wait_x(220),cmd('jump'),cmd('jump_release',hold),cmd('shoot',6,direction=[-math.sqrt(1-dy*dy),dy]),settle(640),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',18),cmd('shoot',6,direction=[-.5,.8660254037844386]),settle(1080,6)]
   add(f'direct-roof-refill-{hold}-{dy}',plan)
 p=copy.deepcopy(c['control_plan']);p[4]=dict(op='wait',trigger=p[4]['trigger']);add('omit-carrier-start',p)
 p=copy.deepcopy(c['control_plan']);p[13]=dict(op='wait',trigger=p[13]['trigger']);add('omit-departure-recoil',p)
 add('ordinary-jump-only',[cmd('axis',value=1),wait_x(220),cmd('jump'),cmd('jump_release',32),settle(1080)])
 add('passive-after-start',[*copy.deepcopy(c['control_plan'][:5]),cmd('axis',value=0),cmd('wait',600)])
 assert len(out)==23
 return out
