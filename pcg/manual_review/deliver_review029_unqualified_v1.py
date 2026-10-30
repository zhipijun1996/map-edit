"""Playable candidates remain explicitly UNQUALIFIED; no fabricated certification."""
import argparse
from pcg.migration import core,physics,godot_package,review029_runtime_v2
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import checked_purpose
from pcg.manual_review.prepare_review029_v1 import AUTH
from pcg.manual_review.finalize_review029_v1 import folder_for

def run(row):
 f=folder_for(row);n=row['reviewId'];eng,cs,authors=physics._engine(f,'approved-r029-'+n+'-unqualified-delivery-v1',physics.FULL_PROTOCOL);items=[];checks=[]
 for i,(c,r,e)in enumerate(eng.run([physics.fresh(c,'unqualified-delivery')for c in cs],'candidate-replay')):
  q=checked_purpose(authors[i],c,r);checks.append(dict(case=c,check=q,evidence=e));items.append(physics._recording(c,r))
 core.write(eng.out/'canonical.json',dict(rows=checks,passed=all(r['check']['ok']for r in checks),qualification='UNQUALIFIED'))
 core.write(f/'playback-cases.json',dict(cases=items));backend=review029_runtime_v2 if n=='171'else godot_package
 backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',f/'playable',stable_id=row['moduleId'])
 try:result=backend.run_package_validation(f/'playable')
 except ValueError as e:result=dict(passed=False,error=str(e),qualification='UNQUALIFIED')
 core.write(f/'package-result.json',result);print(n,'UNQUALIFIED_SAMPLE',result.get('passed'),flush=True)
if __name__=='__main__':
 import sys
 for r in core.read(AUTH/'handoff.json')['rows']:
  if r['reviewId']in sys.argv[1:]:run(r)
