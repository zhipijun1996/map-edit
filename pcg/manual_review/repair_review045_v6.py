"""Native ascent braking, attack-phase refunds, and earlier cavity casts."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .refresh_review045_v1 import rows
from .prepare_review045_v1 import at,end,jump,hook,height,axis
from .repair_review040_v5 import safe_kill
def brake(x,y,sign):
 return at(x,382)+[axis(0),cmd('jump'),dict(op='shoot',direction=[-sign,0],observed_y=dict(value=344,direction='lte'),trigger=dict(state='observed_height',timeout=120)),cmd('jump_release',1)]+at(y,382)
def track(enemy,distance=60):return dict(op='settle',target_x=240,follow_enemy=dict(id=enemy,side=1,distance=distance),deadband=.6,source_native_gain=5.5,trigger=dict(after=0))
def air_ladder():
 enemy='design-air-enemy';p=[axis(0),dict(op='wait',enemy_id=enemy,trigger=dict(state='enemy_attack_ready',timeout=900)),cmd('wait',14),cmd('jump'),height(416,'lte'),dict(op='shoot',aim_cell=dict(kind='enemy',id=enemy,body_offset=[0,16]),enemy_window=dict(id=enemy,minimum_drop=40),trigger=dict(state='enemy_below',timeout=180)),cmd('jump_release',1)]
 for _ in range(2):p+=[track(enemy),dict(op='wait',trigger=dict(state='descending',timeout=180)),height(400),dict(op='shoot',aim_cell=dict(kind='enemy',id=enemy),trigger=dict(state='shot_ready',timeout=180))]
 return p
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v6-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan'];goal=c['exit_port']
  if n=='169':p=(brake(190,365,1)+brake(400,560,1)if a=='entry'else brake(530,395,-1)+brake(350,170,-1))+end(*goal)
  elif n=='55':p=at(130,-42)+[dict(op='settle',target_x=380,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),cmd('jump'),cmd('jump_release',4),dict(op='grapple',aim_target=[330,-40],trigger=dict(state='apex',timeout=120)),dict(op='wait',trigger=dict(after=21,state='free',timeout=240))]+at(380,-42)+end(*goal)
  elif n in {'51','52'}and a=='entry':
   i=next(i for i,v in enumerate(p)if v['op']=='jump_release');assert p[i+1]['op']=='wait';p=p[:i+1]+p[i+2:]
  elif n=='220':
   if z=='A'and a in {'B','C'}:
    if a=='C':p=at(650,492)+at(580,562)+safe_kill('design-ground-enemy',580,562)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+at(441,562)
    else:p=at(270,702)+jump(335,632,hold=10)+at(400,632)+[dict(op='wait',enemy_position=dict(id='design-air-enemy',minimum_x=450,moving_side=1),trigger=dict(state='enemy_x_ready',timeout=900))]+jump(470,562,hold=10)
    p+=air_ladder()
    if a=='B':p+=[track('design-ground-enemy'),dict(op='wait',trigger=dict(state='descending',timeout=180)),height(400),dict(op='shoot',aim_cell=dict(kind='enemy',id='design-ground-enemy'),trigger=dict(state='shot_ready',timeout=180))]
    p+=[dict(op='settle',target_x=24,deadband=.6,source_native_gain=5.5,trigger=dict(after=0)),dict(op='wait',trigger=dict(state='descending',timeout=180)),height(300),dict(op='shoot',direction=[.6,.8],trigger=dict(state='shot_ready',timeout=180))]+end(*goal)
   elif z=='C':
    # Rise vertically beside the ledge; fire before steering into the sentry.
    i=next(i for i,v in enumerate(p)if v.get('enemy_window'));start=i-3;tail=copy.deepcopy(p[i:]);shot=tail[0];shot['aim_cell']['body_offset']=[0,8]
    p=p[:start]+[axis(0),cmd('jump'),height(510,'lte')]+tail
  for v in p:
   if v.get('trigger',{}).get('migration_goal'):v['trigger']['after']=max(1,v['trigger'].get('after',0))
  c['control_plan']=p;c['id']=c['id'].replace('review045-v5','review045-v6').replace('review045-v4','review045-v6')
 doc=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',doc);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for row in rows():
  if row['reviewId']in sys.argv[1:]:apply(row)
