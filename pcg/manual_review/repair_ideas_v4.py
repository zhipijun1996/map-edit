"""Enter the Module before steering sideways away from the TOP Port mouth."""
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .new_ideas_v1 import rows,label
from .prepare_review045_v1 import axis

def main():
 for r in rows():
  if label(r)=='orbit':continue
  f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v4-cases.json',dict(cases=cs))
  for c in cs:
   if c['route_spec']['from_port']=='B':c['control_plan']=[axis(0),cmd('drop_through',1),dict(op='wait',height_threshold=20,trigger=dict(after=1,state='descending_height',timeout=60))]+c['control_plan'][2:]
   c['id']=c['id'].replace('newideas-v5','newideas-v6')
  d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
