"""Same-world pass/shot necessity probes, including paid reasonable options."""
import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle

def alternatives(c):
 out=[];p=c['rule_parameters'];target=p['target'];side=p['side'];end=c['exit_port'][0];prefix=c['control_plan'][:7]
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 v=copy.deepcopy(c['control_plan']);v[12]=cmd('wait');add('omit-selected-shot',v)
 for x in ([400,412,432]if target=='B'else[624,612,592]):
  v=copy.deepcopy(c['control_plan']);v[10]=cmd('jump_release',4);v[11]=wait_x(x,side);add('shoot-before-passing-'+str(x),v)
 for hold in [8,20,30]:
  add('ordinary-M-high-'+str(hold),copy.deepcopy(prefix)+[settle(end),wait_x(p['takeoff'],side),cmd('jump'),cmd('jump_release',hold),ground(),cmd('wait',20)])
 for dy in [0.,.4,.7,.8660254,.98,1.]:
  add('direct-A-high-'+str(dy),[cmd('axis',value=1),wait_x(340),cmd('jump'),cmd('jump_release',24),cmd('shoot',direction=[-side*math.sqrt(1-dy*dy),dy]),settle(end),ground(),cmd('wait',20)])
 for edge in ([432,440]if target=='B'else[592,584]):
  add('M-ground-preopen-extra-shot-'+str(edge),copy.deepcopy(prefix)+[settle(edge),wait_x(edge+4 if side<0 else edge-4,side),ground(),cmd('shoot',aim_cell=dict(kind='bell',id=p['bell'])),ground(),cmd('wait',12)]+copy.deepcopy(c['control_plan'][7:]))
 v=copy.deepcopy(c['control_plan']);v[12]=cmd('shoot',direction=[-side*.6,.8]);add('miss-bell-recoil',v)
 for hold in [20,30]:
  add('over-top-without-opening-'+str(hold),copy.deepcopy(prefix)+[settle(end),wait_x(p['takeoff'],side),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-side*.2,math.sqrt(.96)]),ground(),cmd('wait',20)])
 for hold in [20,30]:
  add('ground-below-gate-around-'+str(hold),[cmd('axis',value=side),cmd('wait',100),ground(),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-side*.3,math.sqrt(.91)]),settle(end),ground(),cmd('wait',20)])
 return out

def preliminary(c):
 p=c['rule_parameters'];wrong=400 if p['target']=='B'else 624;edge=432 if p['target']=='B'else 592
 wanted=['shoot-before-passing-'+str(wrong),'ordinary-M-high-30','direct-A-high-0.98','M-ground-preopen-extra-shot-'+str(edge),'miss-bell-recoil','over-top-without-opening-20','ground-below-gate-around-20']
 by={v['counterexample_kind']:v for v in alternatives(c)};return[by[k]for k in wanted]
