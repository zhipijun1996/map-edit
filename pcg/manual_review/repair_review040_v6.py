"""Late bounded policy revision; native observations and original resources only."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,axis,at,end,jump,height,phase
from .repair_review040_v5 import safe_kill,board,cross_low,rise_c
from .repair_review040_v4 import top223
def prefix_c223():
 return [axis(-1),cmd('jump'),cmd('jump_release',14),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-hub-ground-enemy'),height_threshold=410,trigger=dict(state='descending_height',timeout=180)),axis(0),dict(op='wait',trigger=dict(state='descending',timeout=180)),height(420,'gte'),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-hub-air-enemy'),trigger=dict(state='shot_ready',timeout=180))]+at(470,420)+safe_kill('design-hub-air-enemy',470,420)
def ascend225():
 return at(565,532)+[axis(0),dict(op='shoot',direction=[0,1],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='jump',observed_y=dict(direction='lte',value=482),trigger=dict(state='observed_height',timeout=90)),cmd('shoot',18,direction=[.6,.8]),axis(-1),cmd('jump_release',1)]+at(405,212)
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v6-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];goal=c['exit_port']
  if n=='115':
   if a=='entry':p=safe_kill('design-carrier-enemy',300,582)+at(232,582)+[phase('ferry',[0,.02])]+board(1)+[phase('ferry',[.5,.52])]+end(*goal)
   else:
    p=at(1128,582)
    for _ in range(4):
     block=[phase('ferry',[.5,.52])]+board(-1)+[dict(op='shoot',aim_cell=dict(kind='enemy',id='design-carrier-enemy'),trigger=dict(state='grounded_shot_ready',timeout=180))]+at(1128,582)
     for v in block:v['skip_if_enemy_dead']='design-carrier-enemy'
     p+=block
    p+=[phase('ferry',[.5,.52])]+board(-1)+[phase('ferry',[0,.02])]+end(*goal)
  elif n=='225'and a=='B':p=ascend225()+(rise_c()if z=='C'else jump(200,404,hold=4))+end(*goal)
  elif n=='223':
   if a=='A':p=safe_kill('design-hub-air-enemy',238,420)
   elif a=='C':p=prefix_c223()
   elif a=='B':p=at(700,676)+jump(600,632,hold=10)+safe_kill('design-hub-air-enemy',550,632)+cross_low(325,632,1)
   else:p=[cmd('drop_through')]+at(325,632)+safe_kill('design-hub-air-enemy',340,632)
   if a=='A'and z=='C':p+=jump(570,420,hold=12,shot=[-.98,.199])+safe_kill('design-hub-ground-enemy',570,420)
   elif a=='A'and z=='D':p+=top223()
   elif a=='C'and z in ['A','D']:
    p+=jump(210,420,hold=12,shot=[.98,.199])
    if z=='D':p+=top223()
   else:
    if a in ['A','C']:p+=jump(325,632,hold=4)
    if z in ['A','D']:p+=jump(200,420,hold=24,shot=[.3,.953939])
    if z=='C':p+=jump(570,420,hold=24,shot=[-.3,.953939])+safe_kill('design-hub-ground-enemy',570,420)
    elif z=='D':p+=top223()
    elif z=='B':p+=at(365,632)+cross_low(550,632,-1)
   p+=end(*goal)
  elif n=='220':
   if z=='C':
    p=(at(250,190)+at(285,702)if a=='A'else at(270,702))+jump(335,632,hold=10)+safe_kill('design-air-enemy',400,632)+at(435,632)
    p +=[dict(op='settle',target_x=570,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',14),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-ground-enemy'),enemy_window=dict(id='design-ground-enemy',minimum_drop=50),trigger=dict(state='enemy_below',timeout=180)),dict(op='shoot',direction=[-.98,.199],trigger=dict(state='shot_ready',timeout=180))]+at(680,492)+jump(810,446,hold=10)+end(*goal)
   elif a=='C'and z=='A':
    p=at(610,492)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450),trigger=dict(state='enemy_x_ready',timeout=900)),axis(0),dict(op='shoot',direction=[.6,.8],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='jump',observed_y=dict(direction='lte',value=452),trigger=dict(state='observed_height',timeout=120)),dict(op='settle',target_x=335,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump_release',24),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-air-enemy'),enemy_window=dict(id='design-air-enemy',minimum_drop=15,required_side=1,minimum_actor_y=310),trigger=dict(state='enemy_below',timeout=240)),dict(op='wait',trigger=dict(state='descending',timeout=180)),height(280,'gte'),dict(op='shoot',direction=[.6,.8],trigger=dict(state='shot_ready',timeout=180))]+end(*goal)
   c['generation_rule']['registration_source']='pcg/manual_review/review040_author_v4.py'
  c['control_plan']=p;c['id']=c['id'].replace('review040-v5','review040-v6').replace('review040-v4','review040-v6')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
