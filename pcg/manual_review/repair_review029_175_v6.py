from pcg.migration import core,godot_package
from pcg.manual_review.prepare_review029_v1 import AUTH
from pcg.manual_review.repair_review029_v2 import axis
r=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='175');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v6-cases.json',dict(cases=cs))
for c in cs:
 i=next(i for i,v in enumerate(c['control_plan'])if v['op']=='shoot');c['control_plan'].insert(i,axis(0))
d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
