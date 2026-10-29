from pathlib import Path
from pcg.manual_review.first40_author_v2 import purpose as ordinary
from pcg.manual_review.first30_author_v2 import purpose as air
RUNNER_SCRIPT=Path(__file__).parent/'runtime/review040_runner_v1.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name('first40_author_v2.py'),Path(__file__).with_name('first30_author_v2.py')]
def purpose(case,raw):
 n=case['approved_implementation']['reviewId'];r=air(case,raw)if n=='206'else ordinary(case,raw)
 if not case.get('migration_counter')and raw.get('frames'):
  if n=='115'and not any(f.get('support_id')=='ferry'for f in raw['frames']):r['reasons'].append('actual_carrier_support_missing')
  if n=='206'and not raw.get('review040_release',{}).get('released'):r['reasons'].append('reward_committed_support_release_missing')
 r['ok']=not r['reasons'];return r
