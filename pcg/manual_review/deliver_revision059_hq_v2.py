import sys
from pcg.migration import core,revision059_runtime_v5 as backend
from .continue_revision059_v1 import rows,label
from .finalize_revision059_v1 import folder_for

def run(r):
 f=folder_for(r);p=f/'playable-final-v2';backend.compile_package(f/'module.mapnote.json',f/'playback-cases.json',p,stable_id=r['moduleId']);result=backend.run_package_validation(p);core.write(f/'package-result-final-v2.json',result);print(label(r),'PINNED_NATIVE',result['passed'],flush=True)
if __name__=='__main__':
 for r in rows():
  if label(r)in sys.argv[1:]:run(r)
