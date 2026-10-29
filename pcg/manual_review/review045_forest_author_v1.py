from pathlib import Path
from .first40_author_v2 import purpose as original
from pcg.migration import region_outcomes
RUNNER_SCRIPT=Path(__file__).parent/'runtime/review045_forest_runner_v1.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name('first40_author_v2.py'),Path(region_outcomes.__file__)]
def purpose(case,raw):
 r=original(case,raw)
 if not region_outcomes.satisfied(case,raw):r['reasons'].append('original_region_choice_missing')
 if not case.get('migration_counter')and not case.get('migration_probe'):
  expected=case.get('expected_hook_sequence',[]);actual=[v['source_id']for v in raw.get('original_hook_contacts',[])]
  if expected and actual!=expected:r['reasons'].append('real_hook_sequence_missing')
 r['reasons']=sorted(set(r['reasons']));r['ok']=not r['reasons'];return r
