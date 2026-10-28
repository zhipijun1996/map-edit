"""Real recovery controller alternatives on immutable D05 core geometry."""
import copy
from pathlib import Path
from pcg.prototype.creative_batches.batch30_d05 import api_v3 as core
from pcg.prototype.workshop.rules import cmd,wait_x,ground
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=[Path(core.__file__)]+core.SOURCE_DEPENDENCIES+[HERE/'protocol-v1.json']
RUNNER_SCRIPT=core.RUNNER_SCRIPT
CONTROLS=[(-590,0),(-595,0),(-580,2),(-580,4)]
def fixture(interface=0,control=0):
 c=core.layouts(core.RECIPES[0],interface)[0];takeoff,delay=CONTROLS[control]
 p=copy.deepcopy(c['control_plan'][:9])+[cmd('shoot',direction=[-.95,.3122498999]),cmd('axis',value=1),wait_x(850),cmd('axis',value=0),ground(),cmd('wait',6),cmd('axis',value=-1)]
 q=wait_x(takeoff,-1);q['trigger']['timeout']=650;p+=[q,cmd('axis',value=0),ground(),cmd('wait',6)]
 for n,x in enumerate([-500,-360,-220,80]):
  if n==0 and delay:p+=[cmd('jump'),cmd('axis',delay,value=1),cmd('jump_release',20-delay)]
  else:p+=[cmd('axis',value=1),cmd('jump'),cmd('jump_release',20)]
  p+=[wait_x(x-4),cmd('axis',value=0),ground(),cmd('wait',6)]
 p+=copy.deepcopy(c['control_plan']);c['control_plan']=p;c['id']=f'b30-d05-recovery-v1-i{interface}-c{control}';c['max_frames']=2600
 c['validation_fixture']=dict(kind='missed_bell_actual_lower_recovery_retry',module_enrollment=False,world_reset=False,core_case_id=core.layouts(core.RECIPES[0],interface)[0]['id'],control=control,first_takeoff_x=takeoff,vertical_delay=delay)
 return c
def purpose(c,r):
 why=[];fs=r.get('frames',[]);shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle'];firstshot=shots[0]if shots else None
 floor=next((f for f in fs if firstshot and f['frame']>firstshot['frame']and f.get('grounded')and f.get('support_id')=='Platform3'),None)
 ordered=[];last=floor['frame']if floor else -1
 for pid in ['Platform4','Platform5','Platform6','Platform0']:
  got=next((f for f in fs if f['frame']>last and f.get('grounded')and f.get('support_id')==pid),None)
  if got:ordered.append(dict(id=pid,frame=got['frame']));last=got['frame']
 a=next((f for f in fs if floor and f['frame']>floor['frame']and f.get('grounded')and f.get('support_id')=='Platform0'and abs(f['x']-80)<30 and abs(f['y']-420)<1),None)
 toggle=toggles[0]if toggles else None
 startshot=next((f for f in reversed(shots)if toggle and f['frame']<=toggle['frame']),None)
 firstcatch=next((f for f in fs if startshot and f['frame']>startshot['frame']and f.get('grounded')),None)
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if not floor or not a or len(ordered)!=4:why.append('actual_floor_stairs_A_sequence_missing')
 if not(toggle and toggle.get('running')and toggle.get('airborne')and a and toggle['frame']>a['frame']):why.append('missed_first_shot_did_not_leave_parked_carrier_for_actual_retry')
 if not(firstcatch and firstcatch.get('support_id')=='catch-deck'and firstcatch.get('shot_charges',0)>=1):why.append('retry_first_landing_is_not_refilled_catch_deck')
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage')or r.get('returns'):why.append('harm_or_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<12:why.append('reward_missing')
 return dict(ok=not why,reasons=why,causal=dict(first_wrong_shot=firstshot['frame']if firstshot else None,floor_frame=floor['frame']if floor else None,ordered_stair_supports=ordered,actual_A_frame=a['frame']if a else None,first_carrier_toggle=toggle,retry_air_shot_frame=startshot['frame']if startshot else None,retry_first_support={k:firstcatch.get(k)for k in ['frame','support_id','shot_charges']}if firstcatch else None),behavior={})
