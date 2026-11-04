"""Remaining registered candidates, counted by distinct complete control programs."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import math
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,axis,at,end,jump,phase
from .repair_review040_v5 import rise_c
def board(sign):
 return [axis(0),dict(op='shoot',direction=[-.8*sign,.6],trigger=dict(state='grounded_shot_ready',timeout=180)),dict(op='settle',target_x=350 if sign==1 else 1020,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(dynamic=dict(kind='on_platform',id='ferry'),timeout=180)),axis(0)]
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v9-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan']
  if n=='115':
   s=1 if a=='entry'else -1;stage=240 if s==1 else 1128;window=[0,.02]if s==1 else [.5,.52];other=[.5,.52]if s==1 else [0,.02];p=at(stage,582)
   for _ in range(4):
    block=[phase('ferry',window)]+board(s)+[dict(op='shoot',aim_cell=dict(kind='enemy',id='design-carrier-enemy'),trigger=dict(state='grounded_shot_ready',timeout=180))]+at(stage,582)
    for v in block:v['skip_if_enemy_dead']='design-carrier-enemy'
    p+=block
   p+=[phase('ferry',window)]+board(s)+[phase('ferry',other)]+end(*c['exit_port'])
  elif n=='223':
   for v in p:
    if v.get('direction')==[-.7141428,.7]:v['direction']=[-math.sqrt(1-.735**2),.735]
  elif n=='225':
   if a=='B':
    enemy='design-hub-air-enemy';p=at(532,532)+[axis(0),cmd('jump'),cmd('jump_release',4),dict(op='wait',trigger=dict(state='grounded',timeout=180)),dict(op='wait',enemy_position=dict(id=enemy,minimum_y=395),trigger=dict(state='enemy_y_ready',timeout=900)),dict(op='settle',target_x=492,follow_enemy=dict(id=enemy,side=1,distance=40),deadband=.6,source_native_gain=15,trigger=dict(after=0)),cmd('jump'),dict(op='shoot',aim_cell=dict(kind='enemy',id=enemy,body_offset=[0,8]),enemy_window=dict(id=enemy,minimum_drop=10,required_side=1),trigger=dict(state='enemy_below',timeout=180)),cmd('jump_release',1),dict(op='shoot',direction=[.3,.9539392014],trigger=dict(state='shot_ready',timeout=180))]+at(405,212)+(rise_c()if z=='C'else jump(200,404,hold=4))+end(*c['exit_port'])
   c['generation_rule']['registration_source']='pcg/manual_review/review040_author_v7.py'
  c['control_plan']=p;c['id']=c['id'].replace('review040-v8','review040-v9').replace('review040-v7','review040-v9')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
