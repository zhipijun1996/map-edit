"""Second bounded controls: real geometry, accepted refunds, actual safe lanes."""
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd,wait_x
from .refresh_review045_v1 import rows
from .prepare_review045_v1 import at,end,jump,hook,height,axis,phase
from .repair_review040_v5 import safe_kill
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v2-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];goal=c['exit_port']
  if n=='169':
   # The full body must rise above the 28px thorn before reaching its side.
   for v in p:
    if v['op']=='settle'and v.get('target_x')in [410,520]:v['target_x']=385 if v['target_x']==410 else 550
    t=v.get('trigger',{})
    if 'migration_goal'in t:
     x=t['migration_goal'][0]+4
     if x in [410,520]:t['migration_goal'][0]=(385 if x==410 else 550)-4
  elif n=='115'and a=='entry':
   # Previous rays hit the ferry lip at y562. The native head is at y528.
   for v in p:
    if v.get('aim_cell',{}).get('id')=='design-carrier-enemy':v['aim_cell']['body_offset']=[0,-14]
  elif n=='220'and a=='C'and z=='A':
   b=next(v for v in cs if v['route_spec']['from_port']=='B'and v['route_spec']['to_port']=='A')['control_plan'];i=next(i for i,v in enumerate(b)if v.get('enemy_window'));tail=copy.deepcopy(b[i-3:]);p=at(650,492)+at(580,562)+safe_kill('design-ground-enemy',580,562)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+at(500,562)+tail
  elif n=='223'and a=='C':
   i=next(i for i,v in enumerate(p)if i>40 and v['op']=='settle'and v.get('target_x')in [210,325]);p=safe_kill('design-hub-ground-enemy',660,420)+safe_kill('design-hub-air-enemy',570,420)+at(470,420)+p[i:]
  elif n=='225'and a=='B':
   i=next(i for i,v in enumerate(p)if v.get('enemy_window'));p=p[:i+1]+[axis(-1),cmd('jump_release',1),wait_x(298,-1),axis(0),dict(op='shoot',direction=[0,1],trigger=dict(state='shot_ready',timeout=180))]+at(405,212)+p[i+6:]
  elif n=='42':
   if a=='C':p=at(208,-178)
   else:p=at(232 if a=='entry'else 350,-18)+[axis(0),cmd('jump'),cmd('grapple',1,aim_target=[304,-80]),cmd('jump_release',5),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),dict(op='settle',target_x=208,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',height_threshold=-45,trigger=dict(state='falling_height',timeout=240)),cmd('shoot',direction=[0,1])]+at(208,-178)
   p+=[cmd('native_region_select',4,kind='coin'),cmd('wait',2)]
   if z!='C':p+=[cmd('drop_through')]+at(208,-18)+(at(240,-18)+jump(390,-18,hold=8)if z=='exit'else [])
   p+=end(*goal);c['expected_hook_sequence']=['overlook_side_fruit']if a!='C'else[]
  elif n in {'51','52'}:
   if a=='entry':p=at(-338,-318)+[dict(op='settle',target_x=110,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',4),cmd('grapple',14,aim_target=[-35,-350]),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),cmd('shoot',direction=[-1,0])]+at(110,-294)+hook([330,-350]if n=='51'else[310,-260],0)+[cmd('shoot',direction=[-1,0])]+end(*goal)
   else:p=at(466,goal[1]if n=='51'else-190)+hook([330,-350]if n=='51'else[310,-260],0)+[cmd('shoot',direction=[1,0])]+at(110,-294)+hook([-35,-350],0)+[cmd('shoot',direction=[1,0])]+end(*goal)
  elif n=='50':
   if z=='C':
    p=(at(0,-42)if a=='entry'else[])+[dict(op='settle',target_x=195,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),height(160),cmd('shoot',direction=[-1,0])]+end(*goal);c['expected_hook_sequence']=[]
   elif a=='C':p=at(430,342)+jump(300,332,hold=4)+[cmd('jump'),cmd('grapple',1,aim_target=[120,155]),cmd('jump_release',5),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]+hook([200,-40],0)+[cmd('shoot',direction=[-1 if z=='exit'else 1,0])]+end(*goal)
  if n in {'42','50','51','52'}:c['generation_rule']['registration_source']='pcg/manual_review/review045_forest_author_v2.py'
  for v in p:
   if v.get('trigger',{}).get('migration_goal'):v['trigger']['after']=max(1,v['trigger'].get('after',0))
  c['control_plan']=p;c['id']=c['id'].replace('review045-v1','review045-v2')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for row in rows():
  if row['reviewId']in sys.argv[1:]:apply(row)
