"""Final timing refinements before frozen screening; no holdout has been read."""
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review029_v1 import AUTH,at,end
from .repair_review029_v2 import axis

def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];d=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v6b-cases.json',dict(cases=cs))
 for c in cs:
  p=c['control_plan']
  if n=='176':
   for v in p[:7]:
    if v['op']=='settle'and v['target_x']==330:v['target_x']=280
    if v.get('trigger',{}).get('migration_goal')==[325,417,10,8]:v['trigger']['migration_goal']=[275,417,10,8]
  elif n=='179':
   p[3:5]=[dict(op='shoot',direction=[-.5,.8660254],trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=289),timeout=240))]
  elif n=='193'and c['route_spec']['from_port']=='entry':
   i=next(i for i,v in enumerate(p)if v['op']=='wait'and v.get('trigger',{}).get('dynamic',{}).get('value')==800)
   next(v for v in p[i+1:]if v['op']=='jump_release')['trigger']['after']=8
  elif n=='194':
   c['control_plan']=at(150,420)+[axis(0),dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id='ray-shutter',window=[.78,.805]),timeout=300)),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell')),cmd('wait',10),axis(1),cmd('jump'),cmd('jump_release',8),cmd('shoot',10,direction=[-1,0])]+at(645,420)+end(744,420)
  elif n=='175':
   for v in p:
    if v['op']=='settle'and v['target_x']==1065:v['target_x']=1030
    if v.get('trigger',{}).get('migration_goal')==[1060,416,10,8]:v['trigger']['migration_goal']=[1025,416,10,8]
 d=godot_package.bind_case_behavior(d,cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[1:]:apply(r)
