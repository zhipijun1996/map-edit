from pathlib import Path
from .revision053_three_author_v1 import purpose as previous,SOURCE_DEPENDENCIES,RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('revision053_three_author_v1.py')]
def purpose(case,raw):
    result=previous(case,raw)
    if case.get('explicit_exit_neighbor') and not case.get('migration_counter') and not any(e.get('type')=='bell_open' and e.get('id')=='top-exit-bell' for e in raw.get('plains',{}).get('events',[])):
        result['reasons'].append('actual_top_exit_bell_missing')
    result['ok']=not result['reasons'];return result
