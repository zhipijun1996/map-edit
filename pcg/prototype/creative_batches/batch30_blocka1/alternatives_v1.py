"""Originalshape counterpolicies, reward/safety first; no fake cheapgoal."""
import copy,math
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle

def alternatives(c):
 out=[];forward=c['route_spec']['from_port']=='A';sign=1 if forward else-1;dx=32*c['interface'];bank=c['platforms'][0 if forward else 1];takeoff=205+dx if forward else c['platforms'][1][0]+40;target=c['goal'][0]+7
 def add(kind,plan):
  v=copy.deepcopy(c);v['id']+='-counter-'+kind;v['counterexample_kind']=kind;v['control_plan']=plan;out.append(v)
 source=c['control_plan'];j=next(j for j,q in enumerate(source)if q['op']=='shoot');plan=copy.deepcopy(source);plan[j]=dict(op='wait',trigger=plan[j]['trigger']);add('omit-critical-recoil',plan)
 for hold in [0,4,8,12,20,32]:
  for shift in [0,16]:
   x=takeoff+sign*shift;add(f'ordinary-jump-{hold}-shift{shift}',[cmd('axis',value=sign),wait_x(x,sign),cmd('jump'),cmd('jump_release',hold),settle(target,4)])
 for shift in [-32,0,24]:
  x=takeoff+sign*shift;add('over-roof-upshot-shift'+str(shift),[cmd('axis',value=sign),wait_x(x,sign),cmd('jump'),cmd('jump_release',20),cmd('shoot',5,direction=[0,1]),settle(target,6)])
 add('early-ground-recoil',[cmd('shoot',direction=[-sign*.9886859967,.15]),cmd('wait',8),cmd('axis',value=sign),wait_x(takeoff,sign),cmd('jump'),cmd('jump_release',8),settle(target,6)])
 drop=bank[0]+bank[2]+4 if forward else bank[0]-4
 landing=c['platforms'][1 if forward else 0]
 for offset in [-24,-12,12]:
  x=landing[0]+offset if forward else landing[0]+landing[2]+offset
  p=[cmd('axis',value=sign),wait_x(drop,sign),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=sign),wait_x(x,sign),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=sign),cmd('jump'),cmd('jump_release',32),settle(target,6)]
  add('recovery-bottom-no-shot-'+str(offset),p)
 assert len(out)==20,len(out)
 return out

def preliminary(c):
 names=['omit-critical-recoil','ordinary-jump-32-shift16','over-roof-upshot-shift0','early-ground-recoil','recovery-bottom-no-shot--24']
 out=alternatives(c);chosen=[v for v in out if v['counterexample_kind']in names];assert len(chosen)==5;return chosen
