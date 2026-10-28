"""Second N12 Block-native interface: far landing at entry elevation."""
from pathlib import Path
from . import rules_v1 as source
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.map_directed.block_grid.contracts import declare,validate
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=source.RECIPES;RUNNER_SCRIPT=source.RUNNER_SCRIPT;NATIVE_SCENE=source.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(source.__file__),*source.SOURCE_DEPENDENCIES,Path(__file__),HERE/'second-demand-protocol-v1.json']

def candidate(target='B',control=0):
 c=source.candidate(target,control);c['platforms'][2][1]=480
 c['ports'][2]['position']=[1000,462];c['block_ports']['C']=block_port('C',[7,3],'E',[1000,462])
 cells=set(map(tuple,c['block_grid']['cells']));cells.remove((8,3));cells.add((8,4))
 proj=declare(dict(case=c,ports=c['block_ports'],action_clearance=[]),cells);assert not validate(proj),validate(proj);c['block_grid']=proj['block_grid']
 if target=='C':c['exit_port']=[1000,462];c['goal']=[993,458,14,8]
 c['id']=f'b31-blockn12-v2-i1-{target}-c{control}';c['interface']=1
 c['layout_title']='一空中资源，两种落岸 / 同高远侧口'
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','reward_sites','block_grid','block_ports']})
 c['rule_parameters'].update(interface=1,whole_low_bank_dy=-128,main_floor480=True)
 c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 s=c['map_specification'];s['id']='B31-N12/three-side-port-interface1';s['objective']['physical_layout_sha256']=c['layout_uid'];s['objective']['resource']='Oneoriginalairshot choosesupperinvestmentorfarsameheightbank';s['return_conditions']='OnlyA->B/A->C in sameheightCworld; allother4pairs/rejoin/floorretryUNKNOWN'
 return c

purpose=source.purpose
margin=source.margin
