from pcg.manual_review.continue_revision062_v1 import rows,label
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from pcg.manual_review.prepare_revision060_v1 import wait,follow,supported
from pcg.manual_review.prepare_review045_v1 import at,end,axis
from pcg.manual_review.prepare_ideas_v1 import settle
from pcg.manual_review.prepare_revision058_v2 import jump
from pcg.manual_review.prepare_revision062_new_v1 import height
for r in rows():
 n=label(r)
 if n not in ['s04','s06']:continue
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/revision062_new_author_v3.py';a=c['route_spec']['from_port']
  if n=='s04':
   out=[]
   for v in c['control_plan']:
    if v.get('trigger',{}).get('state')=='r062_ring':out.extend([follow('P'if v['group_id']=='P-bell'else'Q',56),supported('P'if v['group_id']=='P-bell'else'Q')])if any(x.get('trigger',{}).get('state')=='carrier_supported'for x in out)else None
    out.append(v)
   c['control_plan']=out
  else:
   board=at(496,718)+[axis(0),cmd('jump'),cmd('jump_release',24),settle(416),follow('P'),supported('P')]if a=='B'else[axis(0),cmd('drop_through'),settle(112)]+at(112,398)+[cmd('drop_through'),settle(416),follow('P'),supported('P')]
   p=board+[settle(350),wait('observed_height',observed_y=dict(direction='gte',value=650),timeout=180),dict(op='shoot',trigger=dict(after=0,state='r062_mount_edge_shot',timeout=180)),follow('P'),supported('P')]
   if a=='B':p +=[follow('P'),height('P',160,178,up=True,supported=True)]+jump(64,24)+end(64,14)
   else:p +=[follow('P'),height('P',620,642,up=False,supported=True),settle(496)]+end(448,718)
   c['control_plan']=p
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
