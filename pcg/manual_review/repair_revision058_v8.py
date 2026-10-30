"""Short native bell window and shield-side walk-off; preserve immutable older trials."""
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump

def apply(r):
 n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];d=core.read(f/'module.mapnote.json');core.write(f/'history/pre-v8.json',dict(module=d,cases=cs))
 if n=='s07':next(o for o in d['objects']if o['id']=='timed-gate')['mechanics']['openSeconds']=.12
 for c in cs:
  a=c['route_spec']['from_port'];g=c['exit_port'];p=c['control_plan'];c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v6.py'
  if n=='s07':
   for l in c['latches']:l['open_seconds']=.12
   if a=='L':p=at(90,206)+jump(256,24,[-1,0])+at(256,190)+at(366,192)+[settle(374),dict(op='shoot',direction=[-.5,.8660254],native_aim_point=[336,272],height_threshold=210,trigger=dict(after=1,state='descending_shot_height',timeout=120)),settle(448)]+at(448,94)+jump(448,24)+end(*g)
   else:p=[cmd('drop_through',1)]+at(448,94)+[axis(0),dict(op='shoot',direction=[0,-1],trigger=dict(after=1,state='grounded_shot_ready',timeout=120)),dict(op='shoot',direction=[.8,.6],height_threshold=180,trigger=dict(after=1,state='descending_shot_height',timeout=90)),settle(256)]+at(256,190)+at(220,190)+jump(24,24)+end(*g)
  if n=='s02'and a=='B':
   p[0]['trigger'].update(state='revision_board_saw',timeout=1800)
  c.update(control_plan=p,id=c['id']+'-v8')
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
