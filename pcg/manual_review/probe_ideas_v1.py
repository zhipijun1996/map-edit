"""Bounded real clean diagnostics, preserving every raw result."""
import sys
from pcg.migration import core,physics
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from .new_ideas_v1 import rows,label

def run(row,version):
 f=core.REPO/row['outputDirectory'];eng,cs,authors=physics._engine(f,'approved-ideas-'+label(row)+'-canonical-'+version,physics.FULL_PROTOCOL);checks=[];playback=[]
 for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'clean-'+version)for c in cs],'clean-diagnostic')):
  q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e));print(label(row),c['route_spec']['id'],q['ok'],q['reasons'],flush=True)
  if q['ok']:playback.append(physics._recording(c,r))
 core.write(eng.out/'canonical.json',dict(passed=len(playback)==len(cs),rows=checks,independentHoldout=False));core.write(eng.out/'playback-cases.json',dict(cases=playback))
if __name__=='__main__':
 for r in rows():
  if not sys.argv[2:]or label(r)in sys.argv[2:]:run(r,sys.argv[1])
