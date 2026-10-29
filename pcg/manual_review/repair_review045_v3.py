"""Third programs from actual projectile impacts, actor bodies and missing docks."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .refresh_review045_v1 import rows
from .prepare_review045_v1 import at,end,jump,hook,height,axis,phase
from .repair_review040_v9 import board
from .repair_review040_v5 import safe_kill
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v3-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];goal=c['exit_port']
  if n=='115'and a=='entry':
   p=at(228,582)
   for _ in range(5):
    block=[phase('ferry',[0,.02])]+at(308,582)+[axis(0),cmd('jump'),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-carrier-enemy'),observed_y=dict(value=558,direction='lte'),trigger=dict(state='observed_height',timeout=120)),cmd('jump_release',1)]+at(228,582)
    for v in block:v['skip_if_enemy_dead']='design-carrier-enemy'
    p+=block
   p+=at(228,582)+[phase('ferry',[0,.02])]+board(1)+[phase('ferry',[.5,.52])]+end(*goal)
  elif n=='220'and a=='C'and z=='A':p=at(650,492)+at(580,562)+safe_kill('design-ground-enemy',580,562)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=530,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+at(470,562)+[axis(0),dict(op='wait',enemy_id='design-air-enemy',trigger=dict(state='enemy_attack_ready',timeout=900)),cmd('jump'),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-air-enemy',body_offset=[0,16]),enemy_window=dict(id='design-air-enemy',minimum_drop=15,required_side=1),trigger=dict(state='enemy_below',timeout=180)),cmd('jump_release',1),dict(op='wait',trigger=dict(state='descending',timeout=180)),height(300),dict(op='shoot',direction=[.3,.9539392014],trigger=dict(state='shot_ready',timeout=180))]+end(*goal)
  elif n=='223'and a=='C':
   i=next(i for i,v in enumerate(p)if v['op']=='settle'and v.get('target_x')in [210,325]);p=jump(570,420,hold=24)+safe_kill('design-hub-ground-enemy',570,420)+safe_kill('design-hub-air-enemy',570,420)+at(470,420)+p[i:]
  elif n in {'51','52'}:
   if a=='entry':p=at(-324,-318)+[dict(op='settle',target_x=110,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',8),cmd('grapple',8,aim_target=[-35,-350]),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),cmd('shoot',direction=[-.98,.199])]+at(110,-294)+hook([330,-350]if n=='51'else[310,-260],0)+[cmd('shoot',direction=[-1,0])]+end(*goal)
   else:p=at(466,-318 if n=='51'else-190)+[cmd('jump'),cmd('grapple',1,aim_target=[330,-350]if n=='51'else[310,-260]),cmd('jump_release',4),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),cmd('shoot',direction=[.98,.199])]+at(110,-294)+[cmd('jump'),cmd('grapple',1,aim_target=[-35,-350]),cmd('jump_release',4),dict(op='wait',trigger=dict(after=21,state='free',timeout=240)),cmd('shoot',direction=[.98,.199])]+end(*goal)
  elif n=='55':
   p=at(126,-42)+[dict(op='settle',target_x=380,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',6),cmd('grapple',9,aim_target=[330,-40]),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]+at(380,-42)+end(*goal)
  elif n=='50'and a=='C':p=at(385,342)+jump(300,332,hold=4)+[cmd('jump'),cmd('grapple',1,aim_target=[120,155]),cmd('jump_release',5),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]+hook([200,-40],0)+[cmd('shoot',direction=[-1 if z=='exit'else 1,0])]+end(*goal)
  for v in p:
   if v.get('trigger',{}).get('migration_goal'):v['trigger']['after']=max(1,v['trigger'].get('after',0))
  c['control_plan']=p;c['id']=c['id'].replace('review045-v2','review045-v3').replace('review045-v1','review045-v3')
  if n=='220':c['generation_rule']['registration_source']='pcg/manual_review/review045_author_v2.py'
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for row in rows():
  if row['reviewId']in sys.argv[1:]:apply(row)
