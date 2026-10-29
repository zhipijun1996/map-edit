"""Further bounded native controls; no changes to the approved world."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,axis,at,end,jump,height,phase
from .prepare_review_refresh_v1 import kill
def safe_kill(enemy,x,y,count=8):return kill(enemy,x,y,count)+at(x,y)
def board(sign):
 return [axis(0),dict(op='shoot',direction=[-.835164654*sign,.55],trigger=dict(state='grounded_shot_ready',timeout=180)),axis(sign),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='ferry'),timeout=180)),axis(0)]
def cross_low(x,y,direction):
 return [dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',4),dict(op='shoot',direction=[direction,0],height_threshold=565,trigger=dict(state='descending_height',timeout=180))]+at(x,y)
def ascend225():
 return at(565,532)+[axis(0),dict(op='shoot',direction=[0,1],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='jump',observed_y=dict(direction='lte',value=482),trigger=dict(state='observed_height',timeout=90)),cmd('shoot',18,direction=[.6,.8]),axis(-1),cmd('jump_release',1)]+at(405,212)
def rise_c():
 return [dict(op='settle',target_x=448,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),dict(op='jump_release',height_threshold=112,trigger=dict(state='height_at_most',timeout=120))]+at(448,116)
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v5-cases.json',dict(cases=cs))
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
  elif n=='225':
   if a=='B':p=ascend225()+(rise_c()if z=='C'else jump(200,404,hold=4))+end(*goal)
   elif a=='A'and z=='C':p=safe_kill('design-hub-air-enemy',200,404)+at(210,404)+jump(380,212,hold=12,shot=[0,1])+rise_c()+end(*goal)
  elif n=='220':
   if z=='C':
    p=(at(250,190)+at(285,702)if a=='A'else at(270,702))+jump(335,632,hold=10)+safe_kill('design-air-enemy',400,632)+at(435,632)
    p +=[dict(op='settle',target_x=570,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',24),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-ground-enemy'),trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=540),timeout=180))]+at(680,492)+jump(810,446,hold=10)+end(*goal)
   elif a=='C'and z=='A':
    original=c['control_plan'];i=next(i for i,v in enumerate(original)if v.get('enemy_window'));tail=original[i-3:];p=at(650,492)+at(580,562)+safe_kill('design-ground-enemy',580,562)+at(470,562)+tail
  elif n=='223':
   if a=='C':
    old=p;after=next(i for i,v in enumerate(old)if v['op']=='jump');p=safe_kill('design-hub-ground-enemy',680,420,12)+safe_kill('design-hub-air-enemy',470,420)+old[after-1:]
   if z=='B':
    i=next(i for i,v in enumerate(p)if v['op']=='settle'and v.get('target_x')==365);p=p[:i]+at(365,632)+cross_low(550,632,-1)+end(*goal)
  c['control_plan']=p;c['id']=c['id'].replace('review040-v4','review040-v5').replace('review040-v3','review040-v5')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
