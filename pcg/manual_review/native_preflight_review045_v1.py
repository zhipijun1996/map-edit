"""One native package load per successful clean witness, before formal selection."""
import argparse
from pcg.migration import core,physics,godot_package
from .refresh_review045_v1 import rows
def run(row,version):
 n=row['reviewId'];f=core.REPO/row['outputDirectory'];root=core.REPO/'pcg/results'/('approved-r045-'+n+'-canonical-'+version);raw=core.read(root/'canonical.json');assert raw['passed'];assert core.read(root/'playback-cases.json')['cases']
 p=f/('native-preflight-'+version);godot_package.compile_package(f/'module.mapnote.json',root/'playback-cases.json',p,stable_id=row['moduleId'])
 try:r=godot_package.run_package_validation(p)
 except ValueError as error:r=dict(passed=False,error=str(error),failureRetained=True)
 core.write(f/('native-preflight-'+version+'.json'),r);print(n,'NATIVE_PREFLIGHT',r['passed'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--version',required=True);p.add_argument('ids',nargs='+');a=p.parse_args()
 for row in rows():
  if row['reviewId']in a.ids:run(row,a.version)
