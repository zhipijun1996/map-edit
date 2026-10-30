"""Clear the original stair sentry from the rear before ordinary ascending steps."""
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .continue_revision053_v1 import rows,label
from .prepare_review045_v1 import at,end
from .prepare_ideas_v1 import settle
from .repair_review040_v5 import safe_kill

def main():
 r=next(r for r in rows()if label(r)=='220');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-control-v5-cases.json',dict(cases=cs))
 for c in cs:
  if c['route_spec']['to_port']!='C':continue
  p=c['control_plan'];i=next(i for i,v in enumerate(p)if v['op']=='settle'and v.get('target_x')==480)
  p=p[:i]+[settle(470),cmd('jump'),cmd('jump_release',10)]+at(470,562)+[settle(580),cmd('jump'),cmd('jump_release',24)]+at(580,562)+safe_kill('design-ground-enemy',580,562)+[settle(680),cmd('jump'),cmd('jump_release',24)]+at(680,492)+[settle(810),cmd('jump'),cmd('jump_release',24)]+at(810,446)+end(*c['exit_port']);c['control_plan']=p;c['id']+='-stairrear'
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs));core.contract(f/'module.mapnote.json',refresh=True)
if __name__=='__main__':main()
