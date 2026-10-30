import sys
from pcg.migration import core,ideas_runtime_v1 as backend
from .new_ideas_v1 import rows,label

def run(row,version):
 f=core.REPO/row['outputDirectory'];root=core.REPO/'pcg/results'/('approved-ideas-'+label(row)+'-canonical-'+version);assert core.read(root/'canonical.json')['passed'];p=f/('native-preflight-'+version);backend.compile_package(f/'module.mapnote.json',root/'playback-cases.json',p,stable_id=row['moduleId'])
 try:r=backend.run_package_validation(p)
 except ValueError as e:r=dict(passed=False,error=str(e))
 core.write(f/('native-preflight-'+version+'.json'),r);print(label(row),'NATIVE_PREFLIGHT',r['passed'],flush=True)
if __name__=='__main__':
 for r in rows():
  if not sys.argv[2:]or label(r)in sys.argv[2:]:run(r,sys.argv[1])
