import sys
from pcg.migration import core,physics
from pcg.migration.evidence_stream_verify_v1 import verify_report
from .continue_revision063_v1 import rows,label,OUT
from .finalize_revision063_v1 import folder_for
def main():
 for r in rows():
  n=label(r)
  if n not in sys.argv[1:]:continue
  f=folder_for(r);q=core.read(f/'qualification.json');assert q['passed']
  result=verify_report(f,q['report']);assert result['passed']
  core.write(OUT/('verification/rederived-'+n+'.json'),dict(passed=True,name=n,report=q['report'],actualAttempts=result['actualAttempts'],physicsRerun=False,source=physics.artifact(__file__)))
  print(n,'FULL_REPORT_RAW_REDERIVED',flush=True)
if __name__=='__main__':main()
