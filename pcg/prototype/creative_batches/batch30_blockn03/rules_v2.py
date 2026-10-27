from pathlib import Path
from . import rules_v1 as old
from pcg.prototype.factory.core.quality import digest
HERE=Path(__file__).parent
RECIPES=old.RECIPES
RUNNER_SCRIPT=old.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json',Path(__file__)]
purpose=old.purpose

def module_candidate(target='B',control=0):
 c=old.module_candidate(target,control);c['id']=c['id'].replace('-v1-','-v2-');c['generation_rule']['version']=2
 c['moving_platforms'][0]['initial_clock_offset']+=64/140;c['latches'][0]['bell'][0]+=64
 for step in c['control_plan']:
  if step['op']=='shoot':step['trigger']['after']=0
 c['rule_parameters']['initial_center_x']=544;c['rule_parameters']['shot_after_jump_release']=0
 c['layout_uid']=digest({k:c.get(k)for k in ['platforms','ports','moving_platforms','latches','reward_sites','block_grid','block_ports']});c['map_specification']['objective']['physical_layout_sha256']=c['layout_uid']
 return c
