"""Moving missed-catch recovery, real body observation rather than clock phase."""
import copy
from pathlib import Path
from . import rules_v2 as previous
from pcg.prototype.creative_batches.batch30_d05 import api_v3 as core
from pcg.prototype.workshop.rules import cmd,ground
HERE=Path(__file__).parent
SOURCE_DEPENDENCIES=previous.SOURCE_DEPENDENCIES+[Path(previous.__file__),HERE/'moving_runner_v1.gd',HERE/'protocol-v3.json']
RUNNER_SCRIPT=HERE/'moving_runner_v1.gd'
WINDOWS=[[365,390],[390,420],[420,450],[360,365]]
def observe(window,running,vx_max=None):
 query=dict(id='catch-deck',x_range=window,running=running)
 if vx_max is not None:query['vx_max']=vx_max
 return dict(op='wait',trigger=dict(state='grounded',carrier_observation=query,timeout=240))
def fixture(interface=0,control=0):
 c=previous.fixture(interface,2);base=core.layouts(core.RECIPES[0],interface)[0]
 recovery_prefix=c['control_plan'][:-len(base['control_plan'])]
 # Normal air bell hit, followed by deliberately steering left so the carrier
 # starts correctly but cannot catch the actor. No state/position writes.
 p=copy.deepcopy(base['control_plan'][:10])+[cmd('axis',value=-1),ground(),cmd('wait',6)]+copy.deepcopy(recovery_prefix[15:])
 p+=[observe(WINDOWS[control],True,-1),cmd('shoot',aim_cell=dict(kind='bell',id='catch-bell')),observe([355,395],False),cmd('wait',8)]+copy.deepcopy(base['control_plan'])
 c.update(id=f'b30-d05-moving-recovery-v1-i{interface}-c{control}',control_plan=p,max_frames=3000)
 c['validation_fixture']=dict(kind='active_carrier_missed_catch_actual_dock_pause_retry',module_enrollment=False,world_reset=False,control=control,actual_incoming_x_window=WINDOWS[control],original_core_case=base['id'])
 return c
def purpose(c,r):
 why=[];fs=r.get('frames',[]);shots=[f for f in fs if any(e.get('type')=='shot'for e in f.get('accepted',[]))];toggles=[e for e in r.get('workshop',{}).get('events',[])if e['type']=='carrier_toggle'];firstshot=shots[0]if shots else None;firstland=next((f for f in fs if firstshot and f['frame']>firstshot['frame']and f.get('grounded')),None)
 ordered=[];last=firstland['frame']if firstland else -1
 for pid in ['Platform4','Platform5','Platform6','Platform0']:
  got=next((f for f in fs if f['frame']>last and f.get('grounded')and f.get('support_id')==pid),None)
  if got:ordered.append(dict(id=pid,frame=got['frame']));last=got['frame']
 a=next((f for f in fs if firstland and f['frame']>firstland['frame']and f.get('grounded')and f.get('support_id')=='Platform0'and abs(f['x']-80)<30 and abs(f['y']-420)<1),None)
 validtoggles=len(toggles)>=3 and toggles[0]['running']and toggles[0]['airborne']and not toggles[1]['running']and not toggles[1]['airborne']and toggles[2]['running']and toggles[2]['airborne']
 restart=toggles[2]if len(toggles)>=3 else None;restartshot=next((f for f in reversed(shots)if restart and f['frame']<=restart['frame']),None);catch=next((f for f in fs if restartshot and f['frame']>restartshot['frame']and f.get('grounded')),None)
 stopped=next((f for f in fs if len(toggles)>=2 and f['frame']>=toggles[1]['frame']and any(v['id']=='catch-deck'and v['running']is False for v in f.get('workshop',{}).get('carriers',[]))),None);stopbody=next((v for v in stopped.get('moving_platforms',[])if v['id']=='catch-deck'),{})if stopped else{}
 if not r.get('ok'):why.append(r.get('reason','not_stable'))
 if not(firstland and firstland.get('support_id')=='Platform3'):why.append('initial_started_carrier_miss_did_not_reach_lower_floor')
 if len(ordered)!=4 or not a:why.append('actual_lower_stairs_original_A_missing')
 if not(validtoggles and a and toggles[0]['frame']<firstland['frame']<a['frame']<toggles[1]['frame']):why.append('real_start_ground_pause_air_restart_order_missing')
 if not(stopbody and 355<=stopbody['position'][0]<=395):why.append('actual_carrier_not_paused_near_original_dock')
 if not(catch and catch.get('support_id')=='catch-deck'and catch.get('shot_charges',0)>=1):why.append('retry_first_landing_not_real_refilled_catch_deck')
 if r.get('hp')!=5 or r.get('plains',{}).get('player_damage')or r.get('returns'):why.append('harm_or_reset')
 if any(r.get(k,0)for k in ['air_jumps','wall_jumps','grapples']):why.append('forbidden_ability')
 if r.get('workshop',{}).get('coins',0)<12:why.append('reward_missing')
 return dict(ok=not why,reasons=why,causal=dict(initial_lower_landing={k:firstland.get(k)for k in ['frame','support_id']}if firstland else None,ordered_stairs=ordered,actual_A_frame=a['frame']if a else None,carrier_toggles=toggles,actual_dock_pause_position=stopbody.get('position'),retry_first_support={k:catch.get(k)for k in ['frame','support_id','shot_charges']}if catch else None,dock_wait_ticks=toggles[1]['frame']-a['frame']if len(toggles)>=2 and a else None),behavior=dict(shots=r.get('shots'),ticks=r.get('ticks')))
