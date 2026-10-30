from pcg.manual_review.continue_revision062_v1 import rows,label
from pcg.migration import core,godot_package
from pcg.prototype.workshop.rules import cmd
from pcg.manual_review.prepare_revision060_v1 import follow,supported
from pcg.manual_review.prepare_review045_v1 import at,end,axis
from pcg.manual_review.prepare_ideas_v1 import settle
for r in rows():
 n=label(r)
 if n not in ['s04','s06']:continue
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/revision062_new_author_v4.py';p=c['control_plan'];a=c['route_spec']['from_port']
  if n=='s06':
   for v in p:
    if v.get('target_x')==350:v['target_x']=344
   if a=='T':
    j=next(i for i,v in enumerate(p)if v['op']=='drop_through'and i>1);k=next(i for i in range(j+1,len(p))if p[i].get('trigger',{}).get('state')=='carrier_supported');p=p[:j]+[axis(0),cmd('jump'),cmd('jump_release',8),cmd('shoot',1,direction=[-1,0]),follow('P'),supported('P')]+p[k+1:]
  elif a=='B':
   j=next(i for i,v in enumerate(p)if v.get('group_id')=='Q-bell'and v['op']=='shoot');p[j-2:j]=[follow('P',-32),supported('P')]
  else:
   j=next(i for i,v in enumerate(p)if v.get('enemy')=='lower-air-enemy');p=p[:j-1]+p[j+1:]
  c['control_plan']=p
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
