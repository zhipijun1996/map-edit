"""Sixth control revision after the initial program; actual carrier occludes ground ray."""
from pcg.migration import core,godot_package
from pcg.manual_review.prepare_review029_v1 import AUTH
from pcg.prototype.workshop.rules import cmd
r=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='175');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-repair-v8-cases.json',dict(cases=cs))
for c in cs:
 p=c['control_plan'];i=[i for i,v in enumerate(p)if v['op']=='shoot'][2]
 p[i:i]=[cmd('jump'),dict(op='jump_release',height_threshold=360,trigger=dict(state='height_at_most',timeout=60))]
d=godot_package.bind_case_behavior(core.read(f/'module.mapnote.json'),cs);core.write(f/'module.mapnote.json',d);core.contract(f/'module.mapnote.json',refresh=True);core.write(f/'cases.json',dict(cases=cs))
