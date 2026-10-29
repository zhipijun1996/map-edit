import sys
from pcg.migration import core,revision060_runtime_v1,revision061_runtime_v2
from .continue_revision062_v1 import rows,label
from .execution_revision062_v1 import frozen_row

def run(row,version):
 row=frozen_row(row,version);n=label(row);f=core.REPO/row['outputDirectory'];root=core.REPO/'pcg/results'/('approved-r062-'+n+'-canonical-'+version);assert core.read(root/'canonical.json')['passed'];backend=revision060_runtime_v1 if n.startswith('hq')else revision061_runtime_v2;p=f/('native-preflight-'+version);backend.compile_package(f/'module.mapnote.json',root/'playback-cases.json',p,stable_id=row['moduleId'])
 try:r=backend.run_package_validation(p)
 except ValueError as e:r=dict(passed=False,error=str(e))
 core.write(f/('native-preflight-'+version+'.json'),r);print(n,'NATIVE_PREFLIGHT',r['passed'],flush=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[2:]:run(r,sys.argv[1])
