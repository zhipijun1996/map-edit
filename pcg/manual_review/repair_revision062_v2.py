from pcg.manual_review.continue_revision062_v1 import rows,label
from pcg.migration import core,godot_package
from pcg.manual_review.prepare_review045_v1 import end
for r in rows():
 n=label(r)
 if n not in ['hq01','rs10']:continue
 f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];doc=core.read(f/'module.mapnote.json')
 for c in cs:
  c['generation_rule']['registration_source']='pcg/manual_review/revision062_author_v2.py'
  if n=='rs10'and c['route_spec']['from_port']=='B':c['control_plan']=c['control_plan'][:-len(end(336,206))]+end(488,206)
 core.write(f/'cases.json',dict(cases=cs));core.write(f/'module.mapnote.json',godot_package.bind_case_behavior(doc,cs));core.contract(f/'module.mapnote.json',refresh=True)
