import sys
from pcg.migration import core
from .continue_revision063_v1 import rows,label
from .execution_revision063_v1 import frozen_row
def backend(n):
 name='revision058_runtime_v1' if n.startswith(('lt-','lb-')) else 'revision053_runtime_v1' if n=='lift' else 'revision060_runtime_v2' if n=='hq09' else 'revision060_runtime_v1' if n=='hq07' else 'revision062_runtime_v2'
 return __import__('pcg.migration.'+name,fromlist=['compile_package'])
def main():
 for r in rows():
  n=label(r)
  if n not in sys.argv[2:]:continue
  row=frozen_row(r,sys.argv[1]);f=core.REPO/row['outputDirectory'];root=core.REPO/f'pcg/results/approved-r063-{n}-canonical-{sys.argv[1]}';assert core.read(root/'canonical.json')['passed']
  p=f/('native-preflight-'+sys.argv[1]);b=backend(n);b.compile_package(f/'module.mapnote.json',root/'playback-cases.json',p,stable_id=r['moduleId'])
  result=b.run_package_validation(p);core.write(f/('native-preflight-'+sys.argv[1]+'.json'),result);print(n,'NATIVE_PREFLIGHT',result['passed'],flush=True)
if __name__=='__main__':main()
