"""Observe native enemy phase before the chain; recoil clear of descent enemies."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .new_ideas_v1 import rows,label
from .prepare_ideas_v1 import settle,chain_shot
from .prepare_review045_v1 import at,end,axis

def main():
 row=next(r for r in rows()if label(r)=='enemies-3');f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v5-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port'];p=c['control_plan']
  if a=='A'and z=='B':
   p=at(192,590)+[axis(0),dict(op='wait',trigger=dict(after=4,state='chain_prepared',timeout=2400)),settle(235),cmd('jump'),chain_shot('enemy-1',-1,442),cmd('jump_release',1),settle(340),chain_shot('enemy-2',1,370),settle(250),chain_shot('enemy-3',-1,285),settle(320),dict(op='shoot',direction=[0,1],height_threshold=160,final_x=320,trigger=dict(after=4,state='chain_final',timeout=240))]+end(320,14)
   for v in p:
    if v.get('chain_window'):v['aim_cell']['body_offset']=[0,12];v['chain_window']['minimum_drop']=25 if v['chain_window']['id']=='enemy-3'else 40
  elif a=='B':p=[axis(0),cmd('drop_through',1),dict(op='shoot',direction=[1,0],height_threshold=60,trigger=dict(after=4,state='descending_height',timeout=120))]+at(24,590)+end(192,590)
  c['control_plan']=p;c['generation_rule']['registration_source']='pcg/manual_review/ideas_author_v5.py';c['id']='approved-newideas-v7-enemies-3-'+c['route_spec']['id']
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
