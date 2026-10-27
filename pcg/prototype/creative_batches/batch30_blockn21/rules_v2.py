"""Last courtyard rule: clear ceiling before launch and close cold bottom bypass."""
from pathlib import Path
from . import rules_v1 as parent
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=parent.RECIPES;RUNNER_SCRIPT=parent.RUNNER_SCRIPT;NATIVE_SCENE=parent.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(parent.__file__),*parent.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
def prefix():
 return[cmd('axis',value=1),wait_x(200),cmd('axis',value=0),ground(),cmd('shoot',aim_cell=dict(kind='bell',id='courtyard-sequence')),cmd('wait',16),cmd('axis',value=1),wait_x(280),cmd('axis',value=0),ground(),cmd('wait',8),cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[-.6,.8]),settle(576),ground(),cmd('wait',8)]
branch=parent.branch
def candidate(target='B',delay=0):
 c=parent.candidate(target,delay);c['platforms'][0]=[0,736,320,64];c['latches'][0]['sequence_gate']=[352,0,24,928];c['control_plan']=prefix()+branch(target,delay)
 c['id']=c['id'].replace('n21-v1','n21-v2');c['rule_parameters'].update(rule=2,entry_fullbody_clear_shot_x=280,firstgate_bottom=928)
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']});c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid'];c['generation_rule'].update(version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])))
 return c
purpose=parent.purpose
