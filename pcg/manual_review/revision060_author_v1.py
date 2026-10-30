from pathlib import Path
from .ideas_author_v1 import purpose as base,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/revision060_runner_v1.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('revision060_content_v1.py')]
def purpose(case,raw):
 r=base(case,raw)
 if case.get('require_original_interception') and not any(e.get('type')=='original_enemy_projectile_intercepted'and e.get('disposed')and e.get('remaining_after',0)>0 for e in raw.get('workshop',{}).get('interceptions',[])):r['reasons'].append('missing_actual_original_projectile_interception')
 r['ok']=not r['reasons'];return r
