import sys
from pcg.migration import core,revision062_runtime_v1 as backend
from .continue_revision062_v1 import rows,label
from .execution_revision062_v1 import frozen_row
for r in rows():
 if label(r)not in sys.argv[2:]:continue
 row=frozen_row(r,sys.argv[1]);f=core.REPO/row['outputDirectory'];root=core.REPO/'pcg/results'/('approved-r062-'+label(r)+'-canonical-'+sys.argv[1]);assert core.read(root/'canonical.json')['passed'];p=f/('native-preflight-'+sys.argv[1]);backend.compile_package(f/'module.mapnote.json',root/'playback-cases.json',p,stable_id=r['moduleId'])
 try:result=backend.run_package_validation(p)
 except ValueError as e:result=dict(passed=False,error=str(e))
 core.write(f/('native-preflight-'+sys.argv[1]+'.json'),result);print(label(r),'NATIVE_PREFLIGHT',result['passed'],flush=True)
