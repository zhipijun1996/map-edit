"""Live attacks, roof-safe approaches and repeatable native hook returns."""
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd,wait_x
from .refresh_review045_v1 import rows
from .prepare_review045_v1 import at,end,jump,hook,height,axis
from .repair_review040_v5 import safe_kill
def falling(y):return dict(op='wait',height_threshold=y,trigger=dict(state='falling_height',timeout=240))
def initial_cavity():return at(-324,-318)+[dict(op='settle',target_x=110,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',4),cmd('shoot',1,direction=[-1,0]),cmd('wait',9),axis(0)]+hook([-35,-350],0)+[cmd('shoot',direction=[-1,0])]+at(110,-294)
def final_cavity():
 return [cmd('jump'),cmd('grapple',1,aim_target=[-35,-350]),cmd('jump_release',4),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),cmd('shoot',direction=[1,0]),cmd('wait',9),axis(0)]+hook([-35,-350],0)+[axis(-1),wait_x(-110,-1),cmd('shoot',direction=[1,0])]
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v4-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];goal=c['exit_port']
  if n=='169':
   for v in p:
    if v['op']=='settle'and v.get('target_x')in [385,550]:v['target_x']=380 if v['target_x']==385 else 556
    t=v.get('trigger',{})
    if 'migration_goal'in t:
     x=t['migration_goal'][0]+4
     x={385:380,550:556}.get(x,x);t['migration_goal']=[x-.6,379,1.2,6]
  elif n=='220'and a=='C'and z=='A':p=at(650,492)+at(580,562)+safe_kill('design-ground-enemy',580,562)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+at(441,562)+[axis(0),dict(op='wait',enemy_id='design-air-enemy',trigger=dict(state='enemy_attack_ready',timeout=900)),cmd('wait',14),cmd('jump'),height(416,'lte'),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-air-enemy',body_offset=[0,16]),enemy_window=dict(id='design-air-enemy',minimum_drop=15,required_side=1),trigger=dict(state='enemy_below',timeout=180)),cmd('jump_release',1),dict(op='wait',trigger=dict(state='descending',timeout=180)),height(300),dict(op='shoot',direction=[.55,.8351646544],trigger=dict(state='shot_ready',timeout=180))]+end(*goal)
  elif n=='223'and a=='C':
   i=next(i for i,v in enumerate(p)if v['op']=='settle'and v.get('target_x')in [210,325]);p=jump(570,420,hold=24)+safe_kill('design-hub-ground-enemy',570,420)+safe_kill('design-hub-air-enemy',458,420)+at(470,420)+p[i:]
  elif n in {'51','52'}:
   if a=='entry':
    p=initial_cavity()
    if n=='51':p+=[cmd('jump'),cmd('grapple',1,aim_target=[330,-350]),cmd('jump_release',4),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]
    else:p+=hook([310,-260],0)
    p+=[cmd('shoot',direction=[-1,0])]+end(*goal)
   else:
    p=at(466,-318 if n=='51'else-190)+hook([330,-350]if n=='51'else[310,-260],0)
    if n=='51':p+=[axis(-1),falling(-345),cmd('shoot',direction=[.9797958971,.2])]
    else:p+=[cmd('shoot',direction=[.9367496998,.35])]
    p+=at(110,-294)+final_cavity()+end(*goal);c['expected_hook_sequence']=['cavity_ring_b','cavity_ring_a','cavity_ring_a']
  elif n=='50'and a=='C':
   p=at(385,342)+jump(300,332,hold=4)+[cmd('jump'),cmd('grapple',1,aim_target=[120,155]),cmd('jump_release',5),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),axis(0)]+hook([200,-40],0)+[cmd('shoot',direction=[-.98 if z=='exit'else .98,.199])]+end(*goal)
  for v in p:
   if v.get('trigger',{}).get('migration_goal'):v['trigger']['after']=max(1,v['trigger'].get('after',0))
  c['control_plan']=p;c['id']=c['id'].replace('review045-v3','review045-v4').replace('review045-v2','review045-v4')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for row in rows():
  if row['reviewId']in sys.argv[1:]:apply(row)
