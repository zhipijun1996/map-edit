from pcg.manual_review.continue_revision062_v1 import rows,label
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from pcg.manual_review.prepare_revision060_v1 import wait
from pcg.manual_review.prepare_review045_v1 import at,end
from pcg.manual_review.prepare_ideas_v1 import settle
for r in rows():
 if label(r)!='s09':continue
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/revision062_new_author_v2.py'
  if c['route_spec']['from_port']=='L':c['control_plan']=at(90,206)+[wait('r062_saw_low',lookahead=.7),settle(140),wait('observed_height',observed_y=dict(direction='gte',value=242),timeout=180),cmd('shoot',0,direction=[-1,0])]+at(320,398)+[settle(320),cmd('drop_through')]+end(320,590)
  else:
   for i,v in enumerate(c['control_plan']):
    if 'fight_enemy'in v:v['enemy']=v.pop('fight_enemy');v['guard_x']=320;c['control_plan'][i-1]['target_x']=320
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
