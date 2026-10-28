"""Observe actual shot readiness and final carrier departure, not request age."""
import sys
from pcg.migration import core,godot_package
from .prepare_review029_v1 import AUTH,at,end
from .repair_review029_v2 import axis
from pcg.prototype.workshop.rules import cmd

def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];d=core.read(f/'module.mapnote.json');cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v7-cases.json',dict(cases=cs))
 for c in cs:
  p=c['control_plan']
  if n=='175':
   shots=[i for i,v in enumerate(p)if v['op']=='shoot'];p.insert(shots[2],dict(op='wait',trigger=dict(state='grounded_shot_ready',timeout=120)))
  elif n=='193'and c['route_spec']['from_port']=='entry':
   jumps=[i for i,v in enumerate(p)if v['op']=='jump'];i=jumps[-1];p[i:i]=[axis(0),dict(op='wait',trigger=dict(state='carrier_x_gte',timeout=900),carrier_id='carrier',carrier_value=1045),axis(1)]
   c['generation_rule']['registration_source']='pcg/manual_review/review029_author_v3.py'
  elif n=='194':
   # Wait clear of the moving shutter's complete horizontal envelope (130..150).
   # The original single airborne shot retains a real gate+recoil opportunity.
   c['control_plan']=at(180,420)+[axis(0),dict(op='wait',trigger=dict(dynamic=dict(kind='platform_phase',id='ray-shutter',window=[.78,.805]),timeout=300)),axis(1),cmd('jump'),cmd('jump_release',8),cmd('shoot',8,aim_cell=dict(kind='bell',id='short-bell'))]+at(645,420)+end(744,420)
 d=godot_package.bind_case_behavior(d,cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[1:]:apply(r)
