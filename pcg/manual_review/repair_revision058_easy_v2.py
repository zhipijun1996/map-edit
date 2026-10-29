"""Prospective input corrections preserve every approved platform and boundary."""
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision058_v1 import rows,label
from .prepare_review045_v1 import at,end
from .prepare_ideas_v1 import settle
from .prepare_revision058_v2 import jump

def apply(r):
 n=label(r);f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-easy-v2.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];g=c['exit_port'];p=c['control_plan']
  if n=='lt-2x1'and a=='A':p=at(104,78)+jump(192,1)+[dict(op='wait',trigger=dict(after=1,state='airborne',dynamic=dict(kind='actor_x',direction='gte',value=180),timeout=120)),dict(op='shoot',direction=[0,1],height_threshold=64,trigger=dict(after=1,state='descending_height',timeout=120))]+end(*g)
  elif n=='lt-2x2'and a=='A':p=at(100,206)+jump(192,24,[0,1])+end(*g)
  elif n=='lb-2x1':p=at(90 if a=='A'else 158,78)+jump(g[0],1)+end(*g)
  elif n=='lb-2x2'and a=='A':p=at(90,78)+[cmd('drop_through',1),settle(g[0])]+end(*g)
  elif n=='s15':
   if a=='L':p=at(90,206)+jump(g[0],24,[-1,0])+end(*g)
   else:p=at(304,78)+[settle(24),dict(op='shoot',direction=[1,0],height_threshold=110,trigger=dict(after=1,state='descending_height',timeout=120))]+end(*g)
  c['control_plan']=p;c['id']+='-v2'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
