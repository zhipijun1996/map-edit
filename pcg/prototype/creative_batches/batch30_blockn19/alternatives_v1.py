"""Strong exact-world falsifiers; original terrain and door states retained."""
import copy,math
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
def alternatives(c):
 out=[];p=c['control_plan'];shots=[i for i,q in enumerate(p)if q['op']=='shoot'];first,second=shots[:2]
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 for label,ix in [('omit-withdraw',first),('omit-side-switch',second)]:
  v=copy.deepcopy(p);v[ix]=cmd('wait');add(label,v)
 for hold in [0,12,32]:add('zero-gun-ordinary-'+str(hold),[cmd('axis',value=1),wait_x(540),cmd('jump'),cmd('jump_release',hold),settle(1000),ground()])
 for x in [220,280,308]:
  pre=[cmd('axis',value=1),wait_x(x),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='folded-pair')),cmd('wait',20),cmd('axis',value=1),wait_x(500),cmd('axis',value=0)]
  add('shore-preopen-'+str(x),pre+copy.deepcopy(p[7:]))
 for hold in [8,20,32]:
  pre=[cmd('axis',value=1),wait_x(280),cmd('jump'),cmd('jump_release',hold),cmd('shoot',aim_cell=dict(kind='bell',id='folded-pair')),cmd('axis',value=1),wait_x(500),cmd('axis',value=0),ground()]
  add('shore-air-open-'+str(hold),pre+copy.deepcopy(p[8:]))
 for hold in [0,12,32]:
  add('one-gun-no-side-jump-'+str(hold),copy.deepcopy(p[:second])+[cmd('axis',value=1),wait_x(680),cmd('jump'),cmd('jump_release',hold),settle(1000),ground()])
 for hold in [12,20,32]:
  bottom=copy.deepcopy(p[:second])+[cmd('axis',value=1),wait_x(752),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),wait_x(820),cmd('axis',value=0),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',hold),cmd('shoot',direction=[-.3,math.sqrt(.91)]),settle(1000),ground()]
  add('one-swap-floor-side-climb-'+str(hold),bottom)
 for x in [344,400,500]:
  v=copy.deepcopy(p);v[1]=wait_x(x);add('different-underfoot-commit-'+str(x),v)
 for delay in [0,12]:
  v=copy.deepcopy(p);v[second]=cmd('shoot',delay,aim_cell=dict(kind='bell',id='folded-pair',receiver='access'));add('different-side-timing-'+str(delay),v)
 v=copy.deepcopy(p);v[first]=cmd('shoot',direction=[1,0]);add('miss-main-ring',v)
 v=copy.deepcopy(p);v[second]=cmd('shoot',direction=[0,-1]);add('miss-access-ring',v)
 assert len(out)==24,len(out)
 return out
