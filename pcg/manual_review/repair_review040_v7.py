"""Final registered control candidate for 220; remaining bounded route repairs."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,axis,at,end,jump,height,phase
from .repair_review040_v5 import safe_kill,cross_low,rise_c
from .repair_review040_v6 import prefix_c223
from .repair_review040_v4 import top223
def board(sign):
 x=350 if sign==1 else 1020
 return [axis(0),dict(op='shoot',direction=[-.835164654*sign,.55],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='ferry'),timeout=180)),axis(0)]
def ascend225():
 return at(565,532)+[axis(0),dict(op='shoot',direction=[0,1],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='jump',observed_y=dict(direction='lte',value=482),trigger=dict(state='observed_height',timeout=90)),cmd('shoot',18,direction=[.6,.8]),axis(-1),cmd('jump_release',1)]+at(405,212)
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v7-cases.json',dict(cases=cs))
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
   if a=='C'and z=='A':
    p=at(610,492)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900)),axis(0),dict(op='shoot',direction=[.6,.8],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='jump',observed_y=dict(direction='lte',value=452),trigger=dict(state='observed_height',timeout=120)),dict(op='settle',target_x=335,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump_release',24),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-air-enemy'),enemy_window=dict(id='design-air-enemy',minimum_drop=15,required_side=1,minimum_actor_y=310),trigger=dict(state='enemy_below',timeout=240)),dict(op='wait',trigger=dict(state='descending',timeout=180)),height(280,'gte'),dict(op='shoot',direction=[.6,.8],trigger=dict(state='shot_ready',timeout=180))]+end(*goal)
   c['generation_rule']['registration_source']='pcg/manual_review/review040_author_v5.py'
  c['control_plan']=p;c['id']=c['id'].replace('review040-v6','review040-v7').replace('review040-v5','review040-v7')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
