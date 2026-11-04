"""Last low-cost geometric diagnostic before 225's bounded search stops."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from .prepare_review040_v3 import rows,axis,at,end,jump
from .repair_review040_v5 import rise_c
def apply(row):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v8-cases.json',dict(cases=cs))
 for c in cs:
  a,z=c['route_spec']['from_port'],c['route_spec']['to_port']
  if n=='223'and a=='C':
   first=next(v for v in c['control_plan']if v['op']=='jump_release');first['trigger']['after']=24
  elif n=='225':
   if a=='B':c['control_plan']=at(532,532)+[dict(op='wait',enemy_position=dict(id='design-hub-air-enemy',minimum_x=-100000,maximum_x=400,moving_side=-1),trigger=dict(state='enemy_x_ready',timeout=900)),axis(-1),cmd('jump'),cmd('shoot',21,direction=[0,1]),cmd('jump_release',1)]+at(405,212)+(rise_c()if z=='C'else jump(200,404,hold=4))+end(*c['exit_port'])
   c['generation_rule']['registration_source']='pcg/manual_review/review040_author_v6.py'
  c['id']=c['id'].replace('review040-v7','review040-v8')
 d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
if __name__=='__main__':
 import sys
 for r in rows():
  if r['reviewId']in sys.argv[1:]:apply(r)
