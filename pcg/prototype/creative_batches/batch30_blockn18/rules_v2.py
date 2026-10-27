"""Measured upper ray corridor moved; same34px body-excluding aperture."""
from pathlib import Path
from . import rules_v1 as parent
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=parent.RECIPES;RUNNER_SCRIPT=parent.RUNNER_SCRIPT;NATIVE_SCENE=parent.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(parent.__file__),*parent.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
def candidate(target='B',local=False,lo=None):
 c=parent.candidate(target,local,lo)
 assert c['platforms'][9]==[688,0,12,338]and c['platforms'][10]==[688,372,12,98]
 c['platforms'][9]=[688,0,12,358];c['platforms'][10]=[688,392,12,78]
 c['id']=c['id'].replace('n18-v1','n18-v2')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']})
 c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid'];c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 return c
purpose=parent.purpose
phase=parent.phase
tail=parent.tail
prefix=parent.prefix
