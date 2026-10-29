from pcg.manual_review.continue_revision062_v1 import rows,label
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from pcg.manual_review.prepare_revision060_v1 import wait
from pcg.manual_review.prepare_review045_v1 import at,end,axis
from pcg.manual_review.prepare_ideas_v1 import settle
for r in rows():
 if label(r)!='s09':continue
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/revision062_new_author_v7.py'
  if c['route_spec']['from_port']=='L':p=at(90,206)+[wait('r062_saw_low',lookahead=.3),settle(140),wait('observed_height',observed_y=dict(direction='gte',value=242),timeout=180),cmd('shoot',0,direction=[-1,0])]+at(320,398)+[settle(240),wait('observed_height',observed_y=dict(direction='gte',value=520),timeout=180)]+end(320,590)
  else:
   old=c['control_plan'];j=next(i for i,v in enumerate(old)if v.get('trigger',{}).get('state')=='r062_saw_low');p=old[:j]+at(288,398)+[wait('r062_saw_low',lookahead=.5),settle(230),cmd('jump'),cmd('jump_release',24),dict(op='shoot',trigger=dict(after=0,state='r062_s09_return_shot',timeout=180)),settle(80)]+end(24,206)
  c['control_plan']=p
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
