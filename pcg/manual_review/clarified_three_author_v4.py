from pathlib import Path
from pcg.manual_review.clarified_three_author_v1 import purpose as original
RUNNER_SCRIPT=Path(__file__).parent/'runtime/clarified_three_runner_v4.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name(n)for n in ['clarified_three_author_v1.py','review029_author_v1.py','review029_author_v4.py','review029_author_v5.py','first40_author_v2.py']]
def purpose(case,raw):
 r=original(case,raw)
 if case['approved_implementation']['reviewId']=='171'and not case.get('migration_counter')and raw.get('frames'):
  directions=[a['direction'][0]for f in raw['frames']for a in f.get('accepted',[])if a['type']=='shot']
  if len(directions)<6 or any(a*b>=0 for a,b in zip(directions,directions[1:])):r['reasons'].append('171_accepted_shots_not_alternating')
 r['ok']=not r['reasons'];return r
