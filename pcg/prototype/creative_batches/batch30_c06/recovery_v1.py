import copy
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES]
def materialize(control=0,restore=True):
 c=rules.materialize(0,'low',0);high=rules.materialize(0,'high',1)
 failure=copy.deepcopy(high['control_plan'][:4]);failure[3]=cmd('wait',[42,46][control])
 failure += [cmd('shoot',aim_cell=dict(kind='bell',id='branch-pair')),settle(230),ground(),cmd('wait',12)]
 restore_cmd=cmd('shoot',aim_cell=dict(kind='bell',id='branch-pair',receiver='access'))if restore else cmd('wait')
 retry=[restore_cmd,cmd('wait',35),settle(330),wait_x(326),ground(),cmd('wait',8),cmd('jump'),cmd('jump_release',20),cmd('shoot',direction=[0,1]),settle(c['exit_port'][0]),ground(),cmd('wait',10)]
 c['control_plan']=failure+retry;c['max_frames']=1800;c['id']+=f'-recovery-late{[42,46][control]}-'+('restore'if restore else'no-restore')
 c['validation_fixture']=dict(kind='late_high_miss_then_low_recovery',module_enrollment=False,restore=restore,late_wait=[42,46][control])
 return c
def purpose(c,r):
 q=rules.purpose(c,r);fs=r.get('frames',[]);events=q['causal']['actual_pair_events'];claimed=q['causal']['claimed_rewards'];floor=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform3']
 if not floor:q['reasons'].append('no_actual_failure_floor_contact')
 if 'high-cache'in claimed:q['reasons'].append('failed_high_reward_was_already_collected')
 if not any(e.get('open')=='A'and e.get('airborne')for e in events):q['reasons'].append('late_high_world_commitment_missing')
 if c['validation_fixture']['restore']and not any(e.get('open')=='B'and not e.get('airborne')for e in events):q['reasons'].append('real_floor_low_restore_missing')
 q['causal']['actual_floor_resource_samples']=[{k:f.get(k)for k in ['frame','x','y','shot_charges','energy']}for f in floor[::20]]
 q['ok']=not q['reasons'];return q
