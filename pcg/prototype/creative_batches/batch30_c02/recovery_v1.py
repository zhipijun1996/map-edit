import copy
from pathlib import Path
from . import rules_v2 as rules
from pcg.prototype.workshop.rules import cmd,wait_x,ground,settle
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[Path(rules.__file__),*rules.SOURCE_DEPENDENCIES,HERE/'recovery-protocol-v1.json']

def materialize(interface=0,control=0,main_control=0):
 c=rules.materialize(interface,main_control)
 fail=copy.deepcopy(c['control_plan'][:5])+[wait_x(450),cmd('axis',value=0),ground(),cmd('wait',8),cmd('shoot',aim_cell=dict(kind='bell',id='airlock-pair',receiver='access')),cmd('wait',30)]
 back=wait_x([-350,-345][control],-1);back['trigger']['timeout']=480
 steps=[cmd('axis',value=-1),back,cmd('jump'),cmd('jump_release',20),settle(-430),ground(),cmd('wait',8)]
 for x in [-340,-250,-160]:
  steps += [cmd('axis',value=1),cmd('jump'),cmd('jump_release',20),settle(x),ground(),cmd('wait',8)]
 steps += [cmd('axis',value=1),wait_x(80),cmd('axis',value=0),ground(),cmd('wait',12)]
 c['control_plan']=fail+steps+copy.deepcopy(c['control_plan'])
 c['id']+=f'-recovery-r{control}';c['max_frames']=1800
 c['validation_fixture']=dict(kind='intentional_miss_same_world_retry',module_enrollment=False,actual_goal_port='B')
 c['rule_parameters'].update(recovery_control=control,first_stair_takeoff=[-350,-345][control])
 return c

def purpose(c,r):
 q=rules.purpose(c,r);fs=r.get('frames',[]);state=(r.get('workshop',{}).get('paired_gates')or[{}])[0]
 floor=[f for f in fs if f.get('grounded')and f.get('support_id')=='Platform3']
 recovered=[f for f in fs if floor and f['frame']>floor[0]['frame']and f.get('grounded')and f.get('support_id')=='Platform0'and abs(f['x']-80)<=30]
 swaps=[e for e in state.get('events',[])if e.get('type')=='pair_switch']
 if not floor:q['reasons'].append('intentional_miss_did_not_land_on_recovery_floor')
 if not recovered:q['reasons'].append('never_returned_supported_to_original_A')
 if [e.get('open')for e in swaps] != ['B','A','B']:q['reasons'].append('real_restore_and_retry_pair_sequence_missing')
 q['causal'].update(recovery_floor_frames=len(floor),original_A_returned_frames=len(recovered),all_swaps=swaps)
 q['ok']=not q['reasons'];return q
