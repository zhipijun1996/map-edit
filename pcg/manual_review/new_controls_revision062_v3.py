from pcg.manual_review.continue_revision062_v1 import rows,label
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from pcg.manual_review.prepare_revision060_v1 import wait,follow,supported
from pcg.manual_review.prepare_review045_v1 import at,end,axis
from pcg.manual_review.prepare_ideas_v1 import settle
from pcg.manual_review.prepare_revision058_v2 import jump
from pcg.manual_review.prepare_revision062_new_v1 import ring,state,height,clear
for r in rows():
 n=label(r)
 if n not in ['s04','s06','s09']:continue
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  a=c['route_spec']['from_port']
  if n=='s04'and a=='B':
   p=c['control_plan'];j=next(i for i,v in enumerate(p)if v.get('trigger',{}).get('state')=='r062_height');k=next(i for i in range(j+1,len(p))if p[i].get('trigger',{}).get('state')=='carrier_supported');c['control_plan']=p[:j+1]+[ring('P',False),state('P',False)]+at(348,846)+[axis(0),cmd('jump'),cmd('jump_release',24),settle(272),follow('P'),supported('P'),ring('P',True),state('P',True)]+p[k+1:]
  if n=='s06':
   if a=='B':p=at(496,718)+[axis(0),cmd('jump'),cmd('jump_release',24),settle(416),follow('P'),supported('P'),settle(340),wait('observed_height',observed_y=dict(direction='gte',value=620),timeout=180),dict(op='shoot',air_only=True,trigger=dict(after=0,state='r062_mount_shot',timeout=180)),follow('P'),supported('P'),height('P',160,178,up=True,supported=True)]+jump(64,24)+end(64,14)
   else:p=[axis(0),cmd('drop_through'),settle(416),follow('P'),supported('P'),settle(340),wait('observed_height',observed_y=dict(direction='gte',value=620),timeout=180),dict(op='shoot',air_only=True,trigger=dict(after=0,state='r062_mount_shot',timeout=180)),follow('P'),supported('P'),height('P',620,642,up=False,supported=True),settle(496)]+end(448,718)
   c['control_plan']=p
  if n=='s09'and a=='B':
   # Native kill first from the bottom shore; avoid jumping into the diver.
   p=c['control_plan'];c['control_plan']=clear('middle-air-enemy',352)+p
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
