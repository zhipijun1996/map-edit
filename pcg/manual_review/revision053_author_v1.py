from pathlib import Path
from .ideas_author_v1 import purpose as previous,SOURCE_DEPENDENCIES
RUNNER_SCRIPT=Path(__file__).parent/'runtime/revision053_runner_v1.gd'
SOURCE_DEPENDENCIES=[*SOURCE_DEPENDENCIES,Path(__file__).with_name('ideas_author_v1.py')]
def purpose(case,raw):
    result=previous(case,raw)
    if case['approved_implementation']['reviewId']=='196' and 'wall_climb'in case['capabilities'] and raw.get('capability_snapshot',{}).get('wall_enabled'):
        result['reasons']=[r for r in result['reasons']if r!='forbidden_wall_jumps']
        result['ok']=not result['reasons']
    return result
