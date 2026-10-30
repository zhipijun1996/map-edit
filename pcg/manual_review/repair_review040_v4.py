"""Bounded third/fourth controls: safe staging, real coyote and ground recoil."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,axis,at,end,jump,height,phase
from .prepare_review_refresh_v1 import kill
def grounded_board(sign):
 return [axis(0),dict(op='shoot',direction=[-.835164654*sign,.55],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='ferry'),timeout=180)),axis(0)]
def safe_kill(enemy,x,y,count=8):return kill(enemy,x,y,count)+at(x,y)
def top223():
 return at(210,420)+[dict(op='settle',target_x=320,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',4),dict(op='shoot',direction=[-.7141428,.7],trigger=dict(state='apex',timeout=120))]+at(320,260)
def coyote225():
 return at(535,532)+[axis(0),dict(op='shoot',direction=[.4,.916515139],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='jump',observed_y=dict(direction='lte',value=497),trigger=dict(state='observed_height',timeout=90)),axis(-1),cmd('shoot',18,direction=[.2,.9797959]),cmd('jump_release',1)]+at(405,212)
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v4-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];goal=c['exit_port']
  if n=='115':
   if a=='entry':p=safe_kill('design-carrier-enemy',300,582)+[phase('ferry',[0,.02])]+grounded_board(1)+[phase('ferry',[.5,.52])]+end(*goal)
   else:
    p=at(1120,582)
    for _ in range(4):
     block=[phase('ferry',[.5,.52])]+grounded_board(-1)+[dict(op='shoot',aim_cell=dict(kind='enemy',id='design-carrier-enemy'),trigger=dict(state='grounded_shot_ready',timeout=180))]+at(1120,582)
     for v in block:v['skip_if_enemy_dead']='design-carrier-enemy'
     p+=block
    p+=[phase('ferry',[.5,.52])]+grounded_board(-1)+[phase('ferry',[0,.02])]+end(*goal)
  elif n=='225':
   if a=='A'and z=='B':p=at(238,404)+safe_kill('design-hub-air-enemy',238,404)+jump(600,532,hold=12,shot=[-.98,.199])+end(*goal)
   elif a=='B':p=coyote225()+(jump(448,116,hold=12)if z=='C'else jump(200,404,hold=4))+end(*goal)
  elif n=='223':
   if a=='A':p=safe_kill('design-hub-air-enemy',238,420)
   elif a=='C':p=safe_kill('design-hub-ground-enemy',650,420)+safe_kill('design-hub-air-enemy',470,420)
   elif a=='B':p=at(700,676)+jump(600,632,hold=10)+safe_kill('design-hub-air-enemy',550,632)+jump(325,632,hold=12,shot=[.98,.199])
   else:p=[cmd('drop_through')]+at(325,632)+safe_kill('design-hub-air-enemy',340,632)
   if a in ['A','C']:
    if z=='D'and a=='A':p+=top223()+end(*goal);c['control_plan']=p;continue
    if a=='A'and z=='C':p+=jump(570,420,hold=12,shot=[-.98,.199])+safe_kill('design-hub-ground-enemy',570,420)+end(*goal);c['control_plan']=p;continue
    if a=='C'and z=='A':p+=jump(210,420,hold=12,shot=[.98,.199])+end(*goal);c['control_plan']=p;continue
    p+=jump(325,632,hold=4)
   if z in ['A','D']:p+=jump(200,420,hold=24,shot=[.3,.953939])
   if z=='C':p+=jump(570,420,hold=24,shot=[-.3,.953939])+safe_kill('design-hub-ground-enemy',570,420)
   elif z=='D':p+=top223()
   elif z=='B':p+=at(365,632)+jump(550,632,hold=12,shot=[-.98,.199])
   p+=end(*goal)
  elif n=='220':
   if z=='C':p=(at(250,190)+at(285,702)if a=='A'else at(270,702))+jump(335,632,hold=10)+safe_kill('design-air-enemy',400,632)+at(435,632)+jump(565,562,hold=14)+safe_kill('design-ground-enemy',565,562)+jump(680,492,hold=10)+jump(810,446,hold=10)+end(*goal)
   elif a=='C':
    p=at(650,492)+at(580,562)+safe_kill('design-ground-enemy',580,562)
    if z=='B':p+=at(335,632)+safe_kill('design-air-enemy',400,632)+end(*goal)
    else:
     original=c['control_plan'];i=next(i for i,v in enumerate(original)if v.get('enemy_window'));p+=at(500,562)+original[i-3:]
  c['control_plan']=p;c['id']=c['id'].replace('review040-v3','review040-v4').replace('review040-v2','review040-v4')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
