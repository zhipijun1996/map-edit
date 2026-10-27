"""Exact frozen geometry bypass searches, including legitimate miss-left control."""
import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def alternatives(c):
 out=[];p=c['control_plan'];side=-1 if c['route_spec']['to_port']=='B'else 1;target=c['exit_port'][0]
 def add(kind,plan):
  q=copy.deepcopy(c);q['id']+='-counter-'+kind;q['counterexample_kind']=kind;q['control_plan']=plan;out.append(q)
 shots=[i for i,v in enumerate(p)if v['op']=='shoot'];branch=shots[1]
 for label,j in zip(['omit-entry-recoil','omit-branch-shot','omit-outer-recoil'],shots):
  q=copy.deepcopy(p);q[j]=dict(op='wait',trigger=q[j]['trigger']);add(label,q)
 q=copy.deepcopy(p);q[branch]=cmd('shoot',direction=[-side*.5,math.sqrt(.75)]);add('miss-branch-bell',q)
 for hold in [8,20,32]:
  q=copy.deepcopy(p[:branch-2])+[cmd('jump_release',hold),settle(target,4)];add('ordinary-M-jump-'+str(hold),q)
 for dy in [.35,.6,.85,1.]:
  q=copy.deepcopy(p[:branch])+[cmd('shoot',direction=[-side*math.sqrt(1-dy*dy),dy]),settle(target,4)];add('direct-M-to-high-'+str(dy),q)
 for hold in [8,20,32]:
  add('direct-low-entry-'+str(hold),[cmd('axis',value=1),wait_x(225),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-side*.5,math.sqrt(.75)]),settle(target,4)])
 for after in [0,8]:
  add('early-ground-switch-'+str(after),[cmd('shoot',aim_cell=dict(kind='bell',id='wing-pair')),cmd('wait',after)]+copy.deepcopy(p))
 # A fixed second-stage rock is a legitimate destination only if the bridge is redundant.
 for dy in [.5,.8660254]:
  q=copy.deepcopy(p[:branch])+[cmd('shoot',direction=[-side*math.sqrt(1-dy*dy),dy]),wait_x(192 if side<0 else 1088,side),cmd('axis',value=0),ground(),cmd('wait',8)]+[cmd('axis',value=side),cmd('jump'),cmd('jump_release',20),settle(target,0)];add('skip-bridge-to-rock-'+str(dy),q)
 add('ground-M-prefire',[*copy.deepcopy(p[:9]),cmd('shoot',aim_cell=dict(kind='bell',id='wing-pair')),cmd('wait',8),*copy.deepcopy(p[9:])])
 add('recovery-floor-no-shot',[cmd('axis',value=1),wait_x(400),cmd('axis',value=0),ground(),cmd('axis',value=side),settle(target)])
 assert len(out)==20,len(out)
 return out
def preliminary(c):
 names=['omit-branch-shot','miss-branch-bell','ordinary-M-jump-32','direct-M-to-high-0.85','early-ground-switch-0']
 return[v for v in alternatives(c)if v['counterexample_kind']in names]
