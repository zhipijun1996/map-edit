"""Second bounded native policy revision; approved world geometry unchanged."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,axis,at,end,jump,height,phase
from .prepare_review_refresh_v1 import kill
def controlled_jump(x,y,threshold):
 return [dict(op='settle',target_x=x,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),dict(op='jump_release',height_threshold=threshold,trigger=dict(state='height_at_most',timeout=120))]+at(x,y)
def board(sign):
 return[axis(0),cmd('jump'),cmd('jump_release',4),axis(sign),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='ferry'),timeout=180)),axis(0)]
def ascent225():
 return at(535,532)+[dict(op='settle',target_x=420,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',24),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-hub-air-enemy'),enemy_window=dict(id='design-hub-air-enemy',minimum_drop=15),trigger=dict(state='enemy_below',timeout=180)),height(270,'gte'),dict(op='shoot',direction=[0,1],trigger=dict(state='shot_ready',timeout=180))]+at(405,212)
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v2-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];goal=c['exit_port'];p=c['control_plan']
  if n=='202':
   for v in p:
    if v.get('aim_cell',{}).get('receiver')=='return':v['aim_cell']['receiver']='access'
  elif n=='167'and z.startswith('exit_upper'):
   p=at(450,582)+[axis(0),cmd('jump'),dict(op='jump_release',height_threshold=502,trigger=dict(state='height_at_most',timeout=120))]+at(410,512)
   if z=='exit_upper_left':p+=at(270,512)+controlled_jump(220,454,442)
   else:p+=at(420,512)+controlled_jump(550,454,407)
   p+=end(*goal)
  elif n=='115':
   if a=='entry':p=kill('design-carrier-enemy',300,582,8)+at(300,582)+[phase('ferry',[0,.02])]+board(1)+[phase('ferry',[.5,.52])]+end(*goal)
   else:p=at(1060,582)+[phase('ferry',[.5,.52])]+board(-1)+kill('design-carrier-enemy',1015,542,6)+[axis(0),phase('ferry',[0,.02])]+end(*goal)
  elif n=='225':
   if a=='A'and z=='C':p=at(200,404)+kill('design-hub-air-enemy',200,404,8)+jump(380,212,hold=12,shot=[0,1])+jump(448,116,hold=12)+end(*goal)
   elif a=='A'and z=='B':p=at(200,404)+kill('design-hub-air-enemy',200,404,8)+jump(600,532,hold=8,shot=[-.98,.199])+end(*goal)
   elif a=='B':
    p=ascent225()+(jump(448,116,hold=12)if z=='C'else jump(200,404,hold=4))+end(*goal)
   c['generation_rule']['registration_source']='pcg/manual_review/review040_author_v2.py'
  elif n=='223':
   if a=='A':p=kill('design-hub-air-enemy',200,420,8)+at(210,420)+jump(325,632,hold=4)
   elif a=='C':p=kill('design-hub-ground-enemy',700,420,8)+kill('design-hub-air-enemy',650,420,8)+at(500,420)+jump(325,632,hold=4)
   elif a=='B':p=kill('design-hub-air-enemy',700,676,8)+at(700,676)+jump(600,632,hold=10)+jump(325,632,hold=12,shot=[.98,.199])
   else:p=[cmd('drop_through')]+at(325,632)+kill('design-hub-air-enemy',340,632,8)
   if z in ['A','D']:p+=jump(200,420,hold=24,shot=[.3,.953939])
   if z=='C':p+=jump(500,420,hold=24,shot=[-.3,.953939])+kill('design-hub-ground-enemy',500,420,8)
   elif z=='D':p+=at(210,420)+jump(320,260,hold=10,shot=[0,1])
   elif z=='B':p+=jump(600,632,hold=12,shot=[-.98,.199])
   p+=end(*goal)
  elif n=='220':
   if a=='A'and z=='B':continue
   if z=='C':p=(at(250,190)+at(285,702)if a=='A'else at(270,702))+jump(335,632,hold=10)+at(435,632)+kill('design-ground-enemy',435,632,8)+kill('design-air-enemy',400,632,8)+jump(530,562,hold=10)+jump(680,492,hold=10)+jump(810,446,hold=10)+end(*goal)
   elif z=='B':p=kill('design-ground-enemy',800,446,8)+kill('design-air-enemy',800,446,8)+at(650,492)+at(500,562)+at(335,632)+end(*goal)
   elif z=='A':
    p=(at(270,702)+jump(335,632,hold=10)+at(435,632)+kill('design-ground-enemy',435,632,8)+jump(500,562,hold=10)if a=='B'else kill('design-ground-enemy',800,446,8)+at(650,492)+at(500,562))
    p +=[dict(op='settle',target_x=335,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',24),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-air-enemy'),enemy_window=dict(id='design-air-enemy',minimum_drop=15),trigger=dict(state='enemy_below',timeout=180)),dict(op='shoot',direction=[.1,.994987],trigger=dict(state='shot_ready',timeout=180))]+end(*goal)
   c['generation_rule']['registration_source']='pcg/manual_review/review040_author_v2.py'
  c['control_plan']=p;c['id']=c['id'].replace('review040-v1','review040-v2')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
