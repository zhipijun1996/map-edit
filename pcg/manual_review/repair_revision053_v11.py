"""Reach the first hook with the original ordinary jump, avoiding fragile coyote input."""
import sys
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at
from .prepare_ideas_v1 import settle
from .repair_revision053_v2 import hook_done

def apply(row):
 f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v11-cases.json',dict(cases=cs))
 for c in cs:
  if c['route_spec']['from_port']=='entry':
   p=c['control_plan'];i=next(i for i,v in enumerate(p)if v.get('hook_count')==1)
   c['control_plan']=at(-344,-318)+[settle(-140),cmd('jump'),cmd('jump_release',24),dict(op='wait',trigger=dict(after=1,state='airborne',dynamic=dict(kind='actor_x',direction='gte',value=-141),timeout=120)),cmd('grapple',aim_target=[-35,-350]),hook_done(1)]+p[i+1:];c['id']+='-jumpapproach'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:apply(r)
