from pathlib import Path
from pcg.manual_review.review029_author_v5 import purpose as ordinary
from pcg.manual_review.review029_author_v4 import purpose as wave
RUNNER_SCRIPT=Path(__file__).parent/'runtime/clarified_three_runner_v1.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name(n)for n in ['review029_author_v1.py','review029_author_v4.py','review029_author_v5.py','first40_author_v2.py']]
def purpose(case,raw):
 n=case['approved_implementation']['reviewId'];r=(wave if n=='171'else ordinary)(case,raw)
 if not case.get('migration_counter')and raw.get('frames'):
  if n=='171':
   shots=[f['direction'][0]for f in raw.get('fired_commands',[])if f['op']=='shoot'];sign=[1 if v>0 else-1 for v in shots]
   if raw.get('jumps',0)or any(f.get('op')=='jump'for f in raw.get('fired_commands',[])):r['reasons'].append('171_no_jump_intent_violated')
   if len(sign)<6 or any(a==b for a,b in zip(sign,sign[1:])):r['reasons'].append('171_actual_alternating_shots_missing')
  if n=='174'and not any(e.get('type')=='bell_open'for e in raw.get('plains',{}).get('events',[])):r['reasons'].append('174_actual_gate_open_missing')
 r['ok']=not r['reasons'];return r
