"""Low connector headroom: native ground recoil instead of jump through non-Port top."""
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at,end,axis
from .prepare_ideas_v1 import settle

def apply(r):
 n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-easy-v3.json',dict(cases=cs))
 for c in cs:
  a=c['route_spec']['from_port'];g=c['exit_port'];p=c['control_plan']
  c['generation_rule']['registration_source']='pcg/manual_review/revision058_author_v3.py'
  if n=='lb-2x1':
   x=90 if a=='A'else 158;sign=-1 if a=='A'else 1
   p=at(x,78)+[axis(0),cmd('shoot',direction=[sign*.98,.1989974874]),settle(g[0])]+end(*g)
  elif n=='lt-2x1'and a=='A':p=at(80,78)+[axis(0),cmd('shoot',direction=[-.9925461516,-.1218693434]),settle(192),dict(op='shoot',direction=[0,1],trigger=dict(after=1,state='revision_shot_ready',dynamic=dict(kind='actor_x',direction='gte',value=180),timeout=90))]+end(*g)
  c['control_plan']=p;c['id']+='-v3'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
