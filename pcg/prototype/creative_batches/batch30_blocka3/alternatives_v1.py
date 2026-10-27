"""Actual same-world alternatives; no shot-word success whitelist."""
import copy
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle

def alternatives(c):
 out=[];forward=c['route_spec']['from_port']=='A';sign=1 if forward else-1;bank=c['platforms'][0 if forward else 1];target=c['goal'][0]+7
 edge=bank[0]+bank[2]-20 if forward else bank[0]+20
 aim=dict(kind='bell',id='short-bell',**({}if forward else dict(receiver='access')))
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 plan=copy.deepcopy(c['control_plan']);j=next(j for j,q in enumerate(plan)if q['op']=='shoot');plan[j]=dict(op='wait',trigger=plan[j]['trigger']);add('omit-critical-shot',plan)
 for hold in [0,4,8,12,20,32]:
  for shift in [0,12]:
   x=edge+sign*shift;add(f'ordinary-jump-{hold}-shift{shift}',[cmd('axis',value=sign),wait_x(x,sign),cmd('jump'),cmd('jump_release',hold),settle(target,4)])
 for shift in [-32,0,24]:
  add('over-roof-upshot-shift'+str(shift),[cmd('axis',value=sign),wait_x(edge+sign*shift,sign),cmd('jump'),cmd('jump_release',20),cmd('shoot',5,direction=[0,1]),settle(target,6)])
 add('ground-preopen-one-gun',[cmd('axis',value=sign),wait_x(edge,sign),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=aim),cmd('jump'),cmd('jump_release',32),cmd('axis',value=sign),settle(target,4)])
 add('ground-preopen-paid-air-recoil',[cmd('axis',value=sign),wait_x(edge,sign),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=aim),cmd('wait',8),cmd('axis',value=sign),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,direction=[-sign*.8660254,.5]),settle(target,6)])
 drop=bank[0]+bank[2]+4 if forward else bank[0]-4
 other=c['platforms'][1 if forward else 0];x=other[0]-12 if forward else other[0]+other[2]+12
 for shot in [False,True]:
  p=[cmd('axis',value=sign),wait_x(drop,sign),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=sign),wait_x(x,sign),cmd('axis',value=0),ground(),cmd('jump'),cmd('jump_release',32)]
  if shot:p.append(cmd('shoot',8,direction=[-sign*.5,.8660254]))
  p.append(settle(target,6));add('recovery-bottom-'+('recoil'if shot else'no-shot'),p)
 assert len(out)==20
 return out

def preliminary(c):
 names=['omit-critical-shot','ordinary-jump-32-shift12','over-roof-upshot-shift0','ground-preopen-one-gun','recovery-bottom-no-shot']
 out=[v for v in alternatives(c)if v['counterexample_kind']in names];assert len(out)==5;return out
