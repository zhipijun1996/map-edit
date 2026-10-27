"""Final Block station rule: keep the original start bell above its shore."""
from pathlib import Path
from . import rules_v1 as old
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=old.RECIPES;RUNNER_SCRIPT=old.RUNNER_SCRIPT;NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json',HERE/'probe_v2.py']

def candidate(interface=0,control=0,route='near'):
 c=old.candidate(interface,control,route);c['latches'][0]['bell'][1]-=51
 c['id']=c['id'].replace('blockc05-v1','blockc05-v2')
 c['block_adaptation']['bell_follows_terminal_delta']=-51
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['map_specification']=old.specification(c)
 return c

purpose=old.purpose
