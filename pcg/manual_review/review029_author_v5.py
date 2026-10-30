from pathlib import Path
from pcg.manual_review.review029_author_v1 import purpose as ordinary
RUNNER_SCRIPT=Path(__file__).parent/'runtime/review029_runner_v4.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name('review029_author_v1.py'),Path(__file__).with_name('first40_author_v2.py')]
def purpose(case,raw):
 r=ordinary(case,raw)
 if not case.get('migration_counter')and case['approved_implementation']['reviewId']=='175':
  ev=raw.get('plains',{}).get('events',[])
  if not any(e.get('type')=='dock_occupied'and e.get('occupied')for e in ev):r['reasons'].append('actual_native_dock_occupation_missing')
  fs=raw.get('frames',[])
  if not any(f.get('review029_mounted_bells')for f in fs):r['reasons'].append('actual_mounted_bell_missing')
 r['ok']=not r['reasons'];return r
