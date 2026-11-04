"""Use native bell-hood roof; return receiver access is any-side, no new geometry."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump

def apply(r):
 n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];d=core.read(f/'module.mapnote.json');core.write(f/'history/pre-interface-v6.json',dict(cases=cs,module=d))
 if n=='s07':
  next(o for o in d['objects']if o['id']=='timed-gate')['mechanics']['openSeconds']=3
  o=next(o for o in d['objects']if o['id']=='return-bell');o['mechanics'].update(service='ShotLatch.add_access_bell',returnSideOnly=False)
 for c in cs:
  a=c['route_spec']['from_port'];g=c['exit_port'];p=c['control_plan']
  if n=='s15'and a=='L':p=at(80,206)+[settle(360),cmd('jump'),cmd('jump_release',24),cmd('shoot',direction=[-1,0])]+end(*g)
  if n=='s07':
   for l in c['latches']:l.update(open_seconds=3,return_access_side_policy='any')
   if a=='L':p=at(90,206)+jump(256,24,[-1,0])+at(256,190)+at(366,192)+jump(448,1)+[dict(op='shoot',direction=[-.4,.916515139],aim_point=[336,272],xmin=398,trigger=dict(after=1,state='revision_actor',timeout=180))]+end(*g)
   else:p=[cmd('drop_through',1)]+at(448,94)+[axis(0),dict(op='shoot',direction=[0,-1],trigger=dict(after=1,state='grounded_shot_ready',timeout=120)),dict(op='shoot',direction=[.8,.6],trigger=dict(after=1,state='revision_shot_ready',timeout=90)),settle(256)]+at(256,190)+at(220,190)+jump(24,24)+end(*g)
  if n=='s02'and a=='B':
   for v in p:
    if v.get('follow_carrier'):
     v['revision_follow']=v.pop('follow_carrier');v['carrier_offset']=-36
   c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v4.py'
  c['control_plan']=p;c['id']+='-v6'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(d,cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
