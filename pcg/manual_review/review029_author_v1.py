"""Observe real outcomes, authorized abilities and mechanism demonstrations."""
from pathlib import Path
from pcg.manual_review.first40_author_v2 import purpose as footprint
RUNNER_SCRIPT=Path(__file__).parent/'runtime/refresh_runner_v4.gd'
SOURCE_DEPENDENCIES=[Path(__file__).with_name('first40_author_v2.py')]
def purpose(case,raw):
    r=footprint(case,raw);n=case['approved_implementation']['reviewId']
    if 'wall_climb'in case['capabilities']:
        r['reasons']=[x for x in r['reasons']if x!='forbidden_wall_jumps']
    if not case.get('migration_counter')and raw.get('frames'):
        if case['route_spec'].get('require_bell')and not any(e.get('type')=='bell_open'for e in raw.get('plains',{}).get('events',[])):r['reasons'].append('actual_gate_effect_missing')
        if n=='174'and not raw.get('wall_jumps'):r['reasons'].append('actual_native_wall_kick_missing')
        if n in ('175','176','193')and not any(f.get('support_id')in {p['platform_id']for p in case.get('moving_platforms',[])}for f in raw['frames']):r['reasons'].append('actual_carrier_support_missing')
    r['ok']=not r['reasons'];return r
