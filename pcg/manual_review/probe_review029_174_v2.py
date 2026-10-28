"""Use an interior staging point fully on the 29px original right shore."""
from pcg.migration import core
from pcg.manual_review.prepare_review029_v1 import AUTH
from pcg.manual_review.probe_review029_v1 import run
r=next(r for r in core.read(AUTH/'handoff.json')['rows']if r['reviewId']=='174');f=core.REPO/r['outputDirectory'];cs=core.read(f/'cases.json')['cases'];core.write(f/'history/pre-staging-probe-cases.json',dict(cases=cs))
for c in cs:
 c['spawn']=[240,420];c['entry_port']=[240,420];next(p for p in c['ports']if p['id']=='entry')['position']=[240,420]
core.write(f/'cases.json',dict(cases=cs));run(r,'static-conflict-diagnostic-v2')
