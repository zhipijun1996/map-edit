from pathlib import Path
from .revision060_author_v1 import purpose as base,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/revision061_runner_v1.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('revision061_content_v1.py')]
def purpose(case,raw):
 r=base(case,raw)
 if any(p.get('trajectory_kind')=='clockwise_ellipse/v1'for p in case.get('moving_platforms',[])):
  es=[e for f in raw.get('frames',[])for e in f.get('ellipse',[])];
  if not es or any(e['expected_error']>.01 or e['rotation']!=0 for e in es):r['reasons'].append('native_ellipse_binding_mismatch')
 r['ok']=not r['reasons'];return r
