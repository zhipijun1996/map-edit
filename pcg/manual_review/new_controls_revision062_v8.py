from pcg.manual_review.continue_revision062_v1 import rows,label
from pcg.migration import core,godot_package
for r in rows():
 if label(r)!='s06':continue
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  for v in c['control_plan']:
   if v.get('trigger',{}).get('state')=='observed_height'and v.get('observed_y',{}).get('value')==632:v['observed_y']['value']=643
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
