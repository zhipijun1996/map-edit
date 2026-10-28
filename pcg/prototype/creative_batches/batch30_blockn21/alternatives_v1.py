"""Exact-world cold shortcuts, stage omission, paid precommit and gate bypass."""
import copy,math
from . import rules_v2 as rules
from . import control_v1 as old_control
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def prefix():
 c=rules.candidate('C');c['control_plan']=rules.prefix();return old_control.compile_plan(c)
def to_C_relay(fire):
 return[cmd('axis',value=1),wait_x(680),cmd('jump'),cmd('jump_release',20),fire,cmd('axis',value=1),wait_x(896),cmd('axis',value=0),ground(),cmd('wait',8)]
def C_finish():return[cmd('axis',value=1),wait_x(964),cmd('jump'),cmd('jump_release',20),settle(1256),ground(),cmd('wait',10)]
def alternatives(c):
 out=[];p=c['control_plan'];target=c['route_spec']['to_port'];shots=[i for i,q in enumerate(p)if q['op']=='shoot']
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 for kind,ix in [('omit-first',shots[0]),('omit-ingress-recoil',shots[1]),('omit-branch-shot',shots[2])]:
  q=copy.deepcopy(p);q[ix]=cmd('wait');add(kind,q)
 q=copy.deepcopy(p);q[shots[2]]=cmd('shoot',direction=[-.25,math.sqrt(1-.25**2)]if target=='C'else[1,0]);add('free-branch-gun-no-intended-target',q)
 if target=='B':
  for x in [280,300]:
   for hold in [20,32,40]:
    q=[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),ground(),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-.2,math.sqrt(.96)]),cmd('axis',value=0),cmd('wait',10),cmd('axis',value=1),wait_x(336),cmd('axis',value=0),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[.35,math.sqrt(1-.35**2)]),settle(24),ground(),cmd('wait',10)]
    add(f'cold-A-direct-west-{x}-{hold}',q)
  for hold in [32,40]:
   q=copy.deepcopy(p);branchjump=[i for i,v in enumerate(q)if v['op']=='jump'][1];release=branchjump+1;q[release]['trigger']['after']=hold;q[shots[2]]=cmd('wait');add('ordinary-west-relay-'+str(hold),q)
  q=copy.deepcopy(p);q[shots[2]]=cmd('shoot',aim_cell=dict(kind='bell',id='courtyard-sequence',receiver='second'));add('complete-stage2-while-choosing-west',q)
  q=copy.deepcopy(p);q[shots[3]]=cmd('wait');add('omit-west-high-gun',q)
  for hold in [12,32,40]:
   q=copy.deepcopy(p);jump=[i for i,v in enumerate(q)if v['op']=='jump'][-1];q[jump+1]['trigger']['after']=hold;q[shots[3]]=cmd('wait');add('ordinary-west-final-'+str(hold),q)
  for wait in [0,24,60]:add('wait-in-real-courtyard-'+str(wait),prefix()+[cmd('wait',wait)]+copy.deepcopy(p[len(prefix()):]))
  add('walk-west-from-M',prefix()+[cmd('axis',value=-1),settle(24),ground()])
  add('A-no-gun-long-jump-west',[cmd('axis',value=1),wait_x(280),cmd('jump'),cmd('jump_release',40),settle(24),ground()])
  for hold in [12,28]:
   q=copy.deepcopy(p);jump=[i for i,v in enumerate(q)if v['op']=='jump'][1];q[jump+1]['trigger']['after']=hold;add('other-real-west-rise-'+str(hold),q)
 else:
  for hold in [12,20,32]:
   q=prefix()+to_C_relay(cmd('shoot',direction=[-.25,math.sqrt(1-.25**2)]))+[cmd('axis',value=1),wait_x(1064),cmd('shoot',direction=[-.436,math.sqrt(1-.436**2)]),settle(1256),ground(),cmd('wait',10)]
   q[len(prefix())+3]['trigger']['after']=hold;add('paid-under-final-gate-'+str(hold),q)
  add('ground-stage2-then-paid-climb',prefix()+[cmd('axis',value=1),wait_x(680),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='courtyard-sequence',receiver='second')),cmd('wait',16)]+to_C_relay(cmd('shoot',direction=[-.25,math.sqrt(1-.25**2)]))+C_finish())
  initial=prefix();initial[6:6]=[cmd('shoot',aim_cell=dict(kind='bell',id='courtyard-sequence',receiver='second')),cmd('wait',16)];add('precommit-both-from-A',initial+to_C_relay(cmd('shoot',direction=[-.25,math.sqrt(1-.25**2)]))+C_finish())
  for hold in [20,32,40]:add('ordinary-M-to-east-'+str(hold),prefix()+[cmd('axis',value=1),wait_x(680),cmd('jump'),cmd('jump_release',hold),settle(1256),ground()])
  for delay in [4,8,12]:
   q=copy.deepcopy(p);q[shots[2]]['trigger']['after']=delay;add('other-second-shot-delay-'+str(delay),q)
  for hold in [20,32,40]:
   q=copy.deepcopy(p);q[shots[0]]=cmd('wait');firstjump=next(i for i,v in enumerate(q)if v['op']=='jump');q[firstjump+1]['trigger']['after']=hold;add('cold-firstgate-bottom-'+str(hold),q)
  for direction in [[-1,0],[0,1],[0,-1]]:
   q=copy.deepcopy(p);q[shots[2]]=cmd('shoot',direction=direction);add('miss-second-ray-'+str(len(out)),q)
  for x in [660,700]:
   q=copy.deepcopy(p);j=[i for i,v in enumerate(q)if v['op']=='jump'][1];q[j-1]=wait_x(x);add('other-second-takeoff-'+str(x),q)
  add('walk-east-after-only-stage1',prefix()+[cmd('axis',value=1),settle(1256),ground()])
 assert len(out)==24,(target,len(out))
 return out
