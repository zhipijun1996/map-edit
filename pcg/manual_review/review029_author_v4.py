from pathlib import Path
from pcg.manual_review.review029_author_v1 import purpose as ordinary
RUNNER_SCRIPT=Path(__file__).parent/'runtime/review029_runner_v3.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name('review029_author_v1.py'),Path(__file__).with_name('first40_author_v2.py')]
def purpose(case,raw):
 r=ordinary(case,raw)
 if case.get('review029_wave')and not case.get('migration_counter'):
  frames=raw.get('frames',[]);waves=[f.get('review029_wave',{})for f in frames]
  if not any(w.get('triggered')and len(w.get('actors',[]))==2 for w in waves):r['reasons'].append('actual_triggered_wave_missing')
  if waves and waves[0].get('triggered'):r['reasons'].append('enemies_present_before_middle_trigger')
  if not all(a.get('dead')for a in (waves[-1].get('actors',[])if waves else [])):r['reasons'].append('actual_ambush_defeats_missing')
 r['ok']=not r['reasons'];return r
