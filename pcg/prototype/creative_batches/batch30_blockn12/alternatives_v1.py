"""Exact-world low-cost searches; no prescribed aiming words are necessary."""
import copy,math
from pcg.prototype.workshop.counterexamples import alternatives as original
from pcg.prototype.workshop.rules import cmd,wait_x,settle,ground

def alternatives(c):
 out=original(c)
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 end=c['exit_port'][0]
 add('walk-fall-no-shot',[cmd('axis',value=1),settle(end),ground(),cmd('wait',20)])
 for takeoff in [140,205,238]:
  for hold,dy in [(20,1.0),(24,.1)]:
   add(f'other-resource-allocation-{takeoff}-{hold}-{dy}',[cmd('axis',value=1),wait_x(takeoff),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-math.sqrt(1-dy*dy),dy]),settle(end),ground(),cmd('wait',20)])
 for takeoff in [140,228]:
  add('ground-pre-shot-'+str(takeoff),[cmd('axis',value=1),wait_x(takeoff),cmd('axis',value=0),ground(),cmd('shoot',direction=[-.5,math.sqrt(.75)]),cmd('axis',value=1),cmd('jump'),cmd('jump_release',24),settle(end),ground(),cmd('wait',20)])
 return out

def preliminary(c):
 wanted=['omit-shot-4','ordinary-jump-238-30','ordinary-jump-220-20','walk-fall-no-shot','other-resource-allocation-238-20-1.0','other-resource-allocation-205-24-0.1','ground-pre-shot-228']
 by={v['counterexample_kind']:v for v in alternatives(c)}
 return[by[k]for k in wanted]
