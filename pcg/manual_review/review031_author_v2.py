"""Real outcomes, approved body rectangle, authorized native mechanics."""
from pathlib import Path
from pcg.manual_review.first40_author_v2 import purpose as footprint
RUNNER_SCRIPT=Path(__file__).parent/'runtime/review031_runner_v2.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name('first40_author_v2.py')]
def purpose(case,raw):
 r=footprint(case,raw)
 if 'wall_climb'in case['capabilities']:r['reasons']=[x for x in r['reasons']if x!='forbidden_wall_jumps']
 if not case.get('migration_counter')and raw.get('frames'):
  n=case['approved_implementation']['reviewId']
  if case['route_spec'].get('require_bell')and not any(e.get('type')=='bell_open'for e in raw.get('plains',{}).get('events',[])):r['reasons'].append('actual_gate_effect_missing')
  if n=='198':
   supports={f.get('support_id')for f in raw['frames']}
   if not {'carrier','other'}<=supports:r['reasons'].append('actual_two_carrier_support_missing')
 r['ok']=not r['reasons'];return r
