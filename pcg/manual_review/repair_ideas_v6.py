"""Align actual enemy phases, then aim into the real lower body surfaces."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .new_ideas_v1 import rows,label
from .prepare_ideas_v1 import settle,chain_shot
from .prepare_review045_v1 import at,end,axis

def main():
 row=next(r for r in rows()if label(r)=='enemies-3');f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v6-cases.json',dict(cases=cs))
 for c in cs:
  if c['route_spec']['from_port']=='A'and c['route_spec']['to_port']=='B':
   p=at(275,590)+[axis(0),dict(op='wait',trigger=dict(after=4,state='chain_setup',timeout=1800))]+at(192,590)+[axis(0),dict(op='wait',trigger=dict(after=4,state='chain_prepared',timeout=2400)),settle(235),cmd('jump'),chain_shot('enemy-1',-1,442),cmd('jump_release',1),settle(335),chain_shot('enemy-2',1,370),settle(245),chain_shot('enemy-3',-1,285),settle(320),dict(op='shoot',direction=[0,1],height_threshold=160,final_x=320,trigger=dict(after=4,state='chain_final',timeout=240))]+end(320,14)
   for v in p:
    q=v.get('chain_window')
    if q:
     v['aim_cell']['body_offset']={'enemy-1':[0,12],'enemy-2':[-10,14],'enemy-3':[8,12]}[q['id']];q['minimum_drop']=40 if q['id']=='enemy-1'else 35
   c['control_plan']=p
  c['id']='approved-newideas-v9-enemies-3-'+c['route_spec']['id'];c['generation_rule']['registration_source']='pcg/manual_review/ideas_author_v6.py'
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':main()
