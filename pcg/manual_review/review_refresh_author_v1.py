"""Actual approved footprint and world effects, no requested-action shortcuts."""
from pathlib import Path
from pcg.manual_review.first40_author_v2 import purpose as footprint
RUNNER_SCRIPT=Path('pcg/manual_review/runtime/refresh_runner_v1.gd').resolve()
SOURCE_DEPENDENCIES=[Path(__file__).with_name('first40_author_v2.py')]
def purpose(case,raw):
    result=footprint(case,raw)
    if case.get('migration_counter')or not raw.get('frames'):return result
    n=case['approved_implementation']['reviewId'];events=raw.get('plains',{}).get('events',[])
    if n in ('116','146','147','160'):
        ids={l['id']for l in case.get('latches',[])};opened={e['id']for e in events if e.get('type')=='bell_open'}
        if not ids<=opened:result['reasons'].append('required_actual_bell_effect_missing')
    if n=='147':
        ids=[l['id']for l in case['latches']];times={i:min((e['frame']for e in events if e.get('type')=='bell_open'and e['id']==i),default=10**9)for i in ids}
        if len(ids)!=2 or times[ids[0]]>=times[ids[1]]:result['reasons'].append('independent_gate_order_missing')
    result['ok']=not result['reasons'];return result
