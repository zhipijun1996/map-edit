if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import sys
from pcg.migration import core,revision059_runtime_v1 as backend
from .continue_revision059_v1 import rows,label

def run(row,version):
 f=core.REPO/row['outputDirectory'];root=core.REPO/'pcg/results'/('approved-r059-'+label(row)+'-canonical-'+version);assert core.read(root/'canonical.json')['passed'];p=f/('native-preflight-'+version);backend.compile_package(f/'module.mapnote.json',root/'playback-cases.json',p,stable_id=row['moduleId'])
 try:r=backend.run_package_validation(p)
 except ValueError as e:r=dict(passed=False,error=str(e))
 core.write(f/('native-preflight-'+version+'.json'),r);print(label(row),'NATIVE_PREFLIGHT',r['passed'],flush=True)
if __name__=='__main__':
 for r in rows():
  if not sys.argv[2:]or label(r)in sys.argv[2:]:run(r,sys.argv[1])
