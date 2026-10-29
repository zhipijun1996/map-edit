"""Prospective controller/missing-timer fixes; all approved non42 geometry retained."""
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump

def phase():return dict(op='wait',trigger=dict(after=1,state='grounded',dynamic=dict(kind='saw_phase',id='G',window=[.05,.08]),timeout=240))
def apply(r):
 n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];d=core.read(f/'module.mapnote.json');core.write(f/'history/pre-interface-v4-cases.json',dict(cases=cs));core.write(f/'history/pre-interface-v4-module.json',d)
 if n=='s02':
  p=next(p for p in d['generationContract']['ports']if p['id']=='B');p['stagingPosition']=[350,590]
 if n=='s07':next(o for o in d['objects']if o['id']=='timed-gate')['mechanics']['openSeconds']=.24
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];g=c['exit_port'];p=c['control_plan']
  if n=='s02':
   for port in c['ports']:
    if port['id']=='B':port['position']=[350,590]
   if a=='B':c['spawn']=c['entry_port']=[350,590];p=p[:-3]+[] if False else p;p[-9:]=p[-9:]
   if z=='B':c['exit_port']=[350,590];c['goal']=[343,586,14,8];g=c['exit_port'];p=at(80,14)+[cmd('drop_through',1),dict(op='shoot',direction=[-1,0],height_threshold=42,trigger=dict(after=1,state='descending_height',timeout=120)),settle(350)]+end(*g)
   else:
    # Same original carrier; wait until the final approach before ordinary jump.
    for v in p:
     if v.get('exit_y'):v['exit_y']=170
    i=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='carrier_exit');p=p[:i+1]+jump(64,24)+end(*g)
  elif n=='s07':
   for l in c['latches']:l['open_seconds']=.24
   if a=='T':p=[cmd('shoot',direction=[0,-1],trigger=dict(after=1,state='grounded_shot_ready',timeout=120)),cmd('wait',12),cmd('drop_through',1),settle(256)]+at(256,190)+[settle(24)]+end(*g)
  elif n=='s09':
   if a=='L':p=[settle(208)]+at(208,206)+[settle(344)]+at(344,462)+end(*g)
   else:p=at(270,462)+[phase()]+jump(120,24)+at(120,334)+[phase()]+jump(208,24)+at(208,206)+jump(24,24)+end(*g)
  c['control_plan']=p;c['id']+='-v4'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
