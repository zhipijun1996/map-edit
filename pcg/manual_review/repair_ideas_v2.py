"""Original Router compound trigger and bounded live enemy phase preparation."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .new_ideas_v1 import rows,label
from .prepare_ideas_v1 import settle
from .prepare_review045_v1 import at,axis

def main():
 for row in rows():
  n=label(row)
  if n=='enemies-2':continue
  f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v2-cases.json',dict(cases=cs))
  for c in cs:
   p=c['control_plan'];a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];c['id']=c['id'].replace('newideas-v1','newideas-v4').replace('newideas-v3','newideas-v4')
   if n=='orbit':
    i=next(i for i,v in enumerate(p)if v['op']=='shoot'and v.get('aim_cell',{}).get('kind')=='bell');shot=copy.deepcopy(p[i]);shot['jump_same_frame']=True;assert p[i+2]['op']=='jump';p=p[:i]+at(255,230)+[shot,p[i+1]]+p[i+3:]
    if a=='C':p=[axis(0),cmd('drop_through',1),dict(op='wait',height_threshold=20,trigger=dict(after=1,state='descending_height',timeout=60))]+p[2:]
    c['generation_rule']['registration_source']='pcg/manual_review/ideas_author_v3.py'
   elif a=='A'and z=='B':
    floor=c['spawn'][1];p=at(300,floor)+[cmd('jump'),cmd('jump_release',24)]+at(300,floor)+at(192,floor)+p
    i=next(i for i,v in enumerate(p)if v.get('chain_window',{}).get('id')=='enemy-1');p[i]['chain_window']['minimum_drop']=25
   c['control_plan']=p
  d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
