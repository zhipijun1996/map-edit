"""Immutable inputs for every actual relay candidate and native/formal delivery."""
if __name__ == "__main__":
    raise SystemExit("Retired round-specific production entrypoint; use python3 -m module_pipeline and current stable-ID validation inputs.")
import copy,inspect,sys
from pcg.migration import core,physics
from .continue_revision065_lift_v1 import rows,label,ROOT as DRAFT,FINAL,AUTH,OUT
from .revision065_content_v1 import decode
from .native_preflight_revision063_v1 import backend
def folder_for(r):return FINAL/r['moduleId']
def frozen_row(row,version):
 r=copy.deepcopy(row);f=core.REPO/('pcg/manual_review/implementation/revision-065-executed-'+version)/r['moduleId']
 if not f.exists():
  assert len([p for p in(core.REPO/'pcg/results').glob('approved-r065-lift-canonical-*')if list((p/'physics').glob('*.input.json'))])<12
  for n in ['module.mapnote.json','cases.json','migration.json','parameters.json']:core.write(f/n,core.read(DRAFT/r['moduleId']/n))
  core.write(f/'execution-input-freeze.json',dict(version=version,artifacts={n:physics.artifact(f/n)for n in ['module.mapnote.json','cases.json','migration.json','parameters.json']}))
 r['outputDirectory']=core.relative(f);return r
def inherited(module,fn,replacements,**extra):
 s=inspect.getsource(getattr(module,fn))
 for a,b in replacements:s=s.replace(a,b)
 ns={**module.__dict__,**globals(),**extra};exec(compile(s,__file__,'exec'),ns);return ns[fn]
def main():
 action=sys.argv[1];version=sys.argv[2]if len(sys.argv)>2 else'final';row=rows()[0];r=frozen_row(row,version)if action in ['probe','screen','native','freeze','demo']else row;f=core.REPO/r['outputDirectory']
 if action=='probe':
  from . import probe_ideas_v1 as m
  inherited(m,'run',[('approved-ideas-','approved-r065-')])(r,version)
 elif action=='screen':
  from . import screen_review040_v1 as m
  inherited(m,'run',[("'approved-r040-'+row['reviewId']","'approved-r065-'+label(row)")])(r,version)
 elif action=='native':
  run=core.REPO/f'pcg/results/approved-r065-lift-canonical-{version}';assert core.read(run/'canonical.json')['passed'];b=backend('lift');target=f/('native-preflight-'+version);b.compile_package(f/'module.mapnote.json',run/'playback-cases.json',target,stable_id=r['moduleId']);result=b.run_package_validation(target);core.write(f/('native-preflight-'+version+'.json'),result);print('R065_NATIVE_PREFLIGHT',result['passed'],flush=True)
 elif action in ['freeze','demo']:
  from . import finalize_revision063_v1 as m
  inherited(m,'freeze',[('approved-r063','approved-r065'),('revision063_content_v1','revision065_content_v1'),('approved-r063','approved-r065')],ROOT=FINAL)(row,version,demo=action=='demo')
 elif action in ['qualify','deliver']:
  from . import finalize_revision063_v1 as m
  inherited(m,action,[('approved-r063','approved-r065')],ROOT=FINAL)(row)
 else:raise ValueError(action)
if __name__=='__main__':main()
