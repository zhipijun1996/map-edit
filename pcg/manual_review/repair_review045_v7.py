"""Final cavity candidate and bounded safe-ground/lift controls for 220."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .refresh_review045_v1 import rows
from .prepare_review045_v1 import at,end,jump,height,axis
from .repair_review040_v5 import safe_kill
from .repair_review045_v6 import track
def ready_shot(enemy=None,y=400,direction=None):
 v=dict(op='shoot',height_threshold=y,trigger=dict(state='descending_shot_height',timeout=240))
 if enemy:v['aim_cell']=dict(kind='enemy',id=enemy)
 else:v['direction']=direction
 return v
def ladder():
 enemy='design-air-enemy';p=[axis(0),dict(op='wait',enemy_id=enemy,trigger=dict(state='enemy_attack_ready',timeout=900)),cmd('wait',14),cmd('jump'),dict(op='shoot',aim_cell=dict(kind='enemy',id=enemy,body_offset=[0,16]),enemy_window=dict(id=enemy,minimum_drop=40,maximum_actor_y=416),trigger=dict(state='enemy_below',timeout=180)),cmd('jump_release',1)]
 for _ in range(2):p+=[track(enemy),ready_shot(enemy)]
 return p
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v7-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];goal=c['exit_port']
  if n in {'51','52'}and a=='entry':
   i=next(i for i,v in enumerate(p)if v['op']=='jump_release');p=p[:i+1]+[cmd('wait',1)]+p[i+1:]
  elif n=='220':
   if z=='A'and a in {'B','C'}:
    if a=='C':p=at(650,492)+at(580,562)+safe_kill('design-ground-enemy',580,562)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+at(441,562)
    else:p=at(270,702)+jump(335,632,hold=10)+at(400,632)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+jump(470,562,hold=10)
    p+=ladder()
    if a=='B':p+=[track('design-ground-enemy'),ready_shot('design-ground-enemy')]
    p+=[dict(op='settle',target_x=24,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),ready_shot(y=284,direction=[.55,.8351646544])]+end(*goal)
   elif z=='C':
    i=next(i for i,v in enumerate(p)if v['op']=='settle'and v.get('target_x')==435);p=p[:i]+at(400,632)+jump(480,562,hold=10)
    for _ in range(3):p+=[dict(op='shoot',aim_cell=dict(kind='enemy',id='design-ground-enemy',body_offset=[0,8]),trigger=dict(state='grounded_shot_ready',timeout=180),skip_if_enemy_dead='design-ground-enemy'),cmd('jump',1),cmd('jump_release',4)]+at(480,562)
    p+=jump(680,492,hold=10)+jump(810,446,hold=10)+end(*goal)
   c['generation_rule']['registration_source']='pcg/manual_review/review045_author_v3.py'
  for v in p:
   if v.get('trigger',{}).get('migration_goal'):v['trigger']['after']=max(1,v['trigger'].get('after',0))
  c['control_plan']=p;c['id']=c['id'].replace('review045-v6','review045-v7')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for row in rows():
  if row['reviewId']in sys.argv[1:]:apply(row)
