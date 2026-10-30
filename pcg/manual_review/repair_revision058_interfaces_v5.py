"""Prospective native controls; S07 previously unknown timer=.24s; no geometry change."""
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump

def wait(state,**kw):return dict(op='wait',trigger=dict(after=1,state=state,timeout=1200),**kw)
def phase():return dict(op='wait',trigger=dict(after=1,state='grounded',dynamic=dict(kind='saw_phase',id='G',window=[.05,.08]),timeout=240))
def apply(r):
 n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];d=core.read(f/'module.mapnote.json');core.write(f/'history/pre-interface-v5-cases.json',dict(cases=cs));core.write(f/'history/pre-interface-v5-module.json',d)
 if n=='s07':next(o for o in d['objects']if o['id']=='timed-gate')['mechanics']['openSeconds']=.24
 for c in cs:
  a=c['route_spec']['from_port'];g=c['exit_port'];p=c['control_plan'];c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v4.py'
  if n=='s07':
   for l in c['latches']:l['open_seconds']=.24
   if a=='L':p=at(90,206)+jump(256,24,[-1,0])+at(256,190)+at(300,190)+jump(448,4)+[dict(op='shoot',direction=[-.4,.916515139],aim_point=[336,272],trigger=dict(after=1,state='revision_actor',xmin=370))] if False else []
   if a=='L':p=at(90,206)+jump(256,24,[-1,0])+at(256,190)+at(300,190)+jump(448,4)+[dict(op='shoot',direction=[-.4,.916515139],aim_point=[336,272],xmin=370,trigger=dict(after=1,state='revision_actor',timeout=120)),settle(448)]+at(448,94)+jump(448,24)+end(*g)
   else:p=[cmd('drop_through',1)]+at(448,94)+[axis(0),dict(op='shoot',direction=[0,-1],trigger=dict(after=1,state='grounded_shot_ready',timeout=120)),dict(op='shoot',direction=[.8,.6],trigger=dict(after=1,state='revision_shot_ready',timeout=90)),settle(256)]+at(256,190)+at(220,190)+jump(24,24)+end(*g)
  elif n=='s09':
   if a=='L':p=[settle(208)]+at(208,206)+[settle(344)]+at(344,462)+end(*g)
   else:p=at(270,462)+[phase()]+jump(120,24)+at(120,334)+[phase()]+jump(208,24)+at(208,206)+jump(24,24)+end(*g)
  elif n=='s15'and a=='L':p=at(104,206)+[settle(360),cmd('jump'),cmd('jump_release',24),dict(op='shoot',direction=[-1,0],height_threshold=80,trigger=dict(after=1,state='descending_shot_height',timeout=120))]+end(*g)
  c['control_plan']=p;c['id']+='-v5'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
