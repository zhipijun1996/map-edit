"""Final bounded repair: wide inner cavity, overhung throat, lower catch shore."""
from pathlib import Path
from . import rules_v1 as old
from pcg.prototype.workshop.rules import cmd,wait_x,settle
from pcg.prototype.creative_batches.batch30_blockpilot.rules_v1 import block_port
from pcg.prototype.factory.core.quality import digest
from pcg.map_directed.block_grid.contracts import declare,validate
HERE=Path(__file__).parent
RECIPES=old.RECIPES;RUNNER_SCRIPT=old.RUNNER_SCRIPT;NATIVE_SCENE=old.NATIVE_SCENE
SOURCE_DEPENDENCIES=[Path(old.__file__),*old.SOURCE_DEPENDENCIES,HERE/'protocol-v2.json']
rest=old.rest;over=old.over
def candidate(control=0):
 c=old.candidate(control)
 c['platforms']=[[0,736,832,64],[1064,800,128,64],[1216,864,64,64],[96,928,1088,64],[832,816,64,32],[800,624,16,112],[800,624,176,16],[800,704,112,32],[896,640,16,10],[896,694,16,10]]
 c['latches']=[dict(id='near',bell=[864,672],gate=[1048,128,16,800],open_seconds=2.2),dict(id='far',bell=[832,672],gate=[1200,128,16,800],open_seconds=0)]
 b=[1256,846];c['exit_port']=b[:];c['goal']=[1249,842,14,8];c['ports'][1]['position']=b[:]
 c['block_ports']['B']=block_port('B',[9,6],'E',b)
 projected=declare(dict(case=c,ports=c['block_ports'],action_clearance=c['block_reservations']),[tuple(v)for v in c['block_grid']['cells']]);assert not validate(projected),validate(projected);c['block_grid']=projected['block_grid']
 c['reward_sites'][0].update(position=b[:],region=[1238,838,36,16])
 aim=dict(kind='bell',id='far')
 c['control_plan']=[cmd('axis',value=1),wait_x(772),cmd('jump'),cmd('jump_release',20),wait_x(852),*rest(),cmd('axis',value=1),wait_x(1035),cmd('shoot',[2,3][control],aim_cell=aim),cmd('wait',8),cmd('axis',value=1),wait_x(1140),*rest(),cmd('axis',value=-1),wait_x(1080,-1),*rest(),cmd('axis',value=-1),cmd('jump'),cmd('shoot',11,aim_cell=aim),cmd('jump_release'),settle(1256,0)]
 c['id']=c['id'].replace('blockn10-v1','blockn10-v2')
 c['layout_uid']=digest({k:c[k]for k in ['platforms','ports','latches','reward_sites','block_grid','block_ports']})
 c['rule_parameters']=dict(control=control,first_wall_drop_shot_after=[2,3][control],second_left_jump_shot_after=11,near_seconds=2.2,near_collision_original_size=[28,34],mouth=[896,650,16,44],overhang=[912,624,64,16],inner_cavity_vertical=[640,704],receiver_pair_centres=[[864,672],[832,672]],M=c['platforms'][1][:],B=c['platforms'][2][:],recovery_floor_unchanged=True)
 c['generation_rule']=dict(id='batch30/N10',version=2,source_path=str(Path(__file__).relative_to(HERE.parents[3])),parameters=c['rule_parameters'])
 s=c['map_specification'];s['id']='batch30/N10/explicit-lower-exit-receiver-window';s['objective'].update(physical_layout_sha256=c['layout_uid'],originalconcept_high_B_modified_to_lower_exit=True,originalconcept_high_B_modified_to_sameheight=False)
 s['risk_reward']['reward_sites']=c['reward_sites'];s['return_conditions']='B->A/failedfloorretry/seams/fullMapUNKNOWN; lateMrecapturefixtureseparate'
 return c
def purpose(c,r):
 q=old.purpose(c,r);n=q['causal']['near_state_when_far_hit'];q['causal']['configured_near_ticks']=round(c['latches'][0]['open_seconds']*60)
 q['causal']['actual_current_near_window_age_ticks']=(n['clock']-n['opened_at'])*60 if n else None
 q['causal']['near_window_age_is_original_clock_not_antipinch']=True
 return q
