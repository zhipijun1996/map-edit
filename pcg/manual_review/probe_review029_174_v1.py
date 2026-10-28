"""Diagnose native wall route while preserving the explicit Port type conflict."""
from pcg.migration import core,physics
from pcg.manual_review.prepare_review029_v1 import AUTH,at
from pcg.manual_review.probe_review029_v1 import run
r=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='174');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/partial-materializer-cases.json',dict(cases=cs))
for c in cs:
 c['control_plan']=at(80,420)+c['control_plan'][2:]
 for v in c['control_plan']:
  if v['op']=='axis':v['cancel_settle']=True
 c['id']='approved-review029-diagnostic-174';c['max_frames']=2400
 c.pop('recorded_frames',None)
core.write(f/'cases.json',dict(cases=cs));core.write(f/'static-conflict.json',dict(passed=False,reason='approved exit ROCK but the existing supporting Cell is one-way platform',designVersion=r['designVersion'],exit=next(p for p in core.read(r['designFile'])['ports']if p['id']=='exit'),support=next(o for o in core.read(r['designFile'])['visualObjects']if o['type']=='platform'),productionApproval=False,geometryChangedToResolve=False))
run(r,'static-conflict-diagnostic-v1')
