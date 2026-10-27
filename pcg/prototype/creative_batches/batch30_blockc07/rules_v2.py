"""Same physical version, explicit upper ownership for paid jump alternative."""
from pathlib import Path
from . import rules_v1 as old
from pcg.map_directed.block_grid.contracts import raster,connected
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=old.RECIPES;RUNNER_SCRIPT=old.RUNNER_SCRIPT;NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json',HERE/'probe_v2.py']

def candidate(interface=0,control=0):
 c=old.candidate(interface,control);space=[128,-320,384,400];c['block_reservations'].append(space)
 cells=set(map(tuple,c['block_grid']['cells']))|raster(space)
 assert connected(cells)
 for p in c['block_ports'].values():assert tuple(p['grid']['cell'][i]+p['normal'][i]for i in range(2))not in cells
 c['block_grid']['cells']=sorted(map(list,cells));c['id']=c['id'].replace('blockc07-v1','blockc07-v2')
 c['block_adaptation']['paid_jump_upper_reservation']=space
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 c['map_specification']=old.specification(c)
 return c

purpose=old.purpose
