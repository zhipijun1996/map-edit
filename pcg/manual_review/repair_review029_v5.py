if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd,settle
from .prepare_review029_v1 import AUTH,at,end
from .repair_review029_v2 import axis

def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];d=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v5-cases.json',dict(cases=cs))
 for c in cs:
  p=c['control_plan']
  if n=='175':c['generation_rule']['registration_source']='pcg/manual_review/review029_author_v5.py'
  elif n=='179':c['control_plan']=at(190,168)+[axis(1),dict(op='wait',trigger=dict(dynamic=dict(kind='actor_x',direction='gte',value=289),timeout=240)),cmd('shoot',direction=[-.5,.8660254])]+end(616,552)
  elif n=='173'and c['route_spec']['from_port']=='entry':
   for v in p:
    if v['op']=='shoot'and 'direction'in v:v['direction']=[0,1]
  elif n=='165':
   c['control_plan']=at(265,282)+[axis(1),cmd('jump'),cmd('jump_release',4),cmd('shoot',10,aim_cell=dict(kind='bell',id='windchime_plains_windchime_well'))]+at(430,282)+end(616,282)
  elif n=='194':
   c['control_plan']=at(200,420)+[axis(0),dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id='ray-shutter',window=[.78,.805]),timeout=300)),cmd('shoot',aim_cell=dict(kind='bell',id='short-bell')),axis(1),cmd('jump',1),cmd('jump_release',8),cmd('shoot',10,aim_cell=dict(kind='bell',id='short-bell'))]+at(645,420)+end(744,420)
  elif n=='193'and c['route_spec']['from_port']=='exit':
   i=next(i for i,v in enumerate(p)if v['op']=='shoot'and v.get('direction')==[.5,.8660254]);p[i:i+1]=[cmd('jump_release',12),cmd('shoot',6,direction=[.5,.8660254])]
 for c in cs:
  for v in c['control_plan']:
   if v['op']=='axis':v['cancel_settle']=True
 d=godot_package.bind_case_behavior(d,cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[1:]:apply(r)
