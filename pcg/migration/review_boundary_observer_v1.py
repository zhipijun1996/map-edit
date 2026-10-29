"""Read-only repair of the 206 AIR observer leaking into ROCK local probes.

No raw flag is rewritten. All crossing/aperture/world-outcome gates remain in
physics.crossing; this computes only the original grounded terminal predicate.
"""
import math
VERSION='sha256:db852c43535585c6f055669a7e702580a8abdd3aebd8471597606445c3bca4af'
def observe(case,raw):
 p=case.get('migration_probe',{});a=case.get('approved_first30',{})
 if a.get('reviewId')!='206' or a.get('designVersion')!=VERSION:return None
 if p.get('kind')!='local_boundary' or p.get('portId')!='entry' or p.get('normal')!=[-1,0] or p.get('boundary')!=[0,406] or p.get('direction')not in ('ingress','egress'):return None
 if case.get('air_goal_probe') or not any(q.get('id')==case.get('route_spec',{}).get('to_port') and q.get('surface')=='AIR' and q.get('face')=='BOTTOM' for q in case.get('air_port_contracts',[])):return None
 if raw.get('ok') or raw.get('reason')!='frame_budget' or not raw.get('plan_completed') or raw.get('plan_error') or not raw.get('module_definition_valid') or raw.get('goal_stable_frames')!=0:return None
 if raw.get('hp')!=5 or raw.get('dead') or not raw.get('safe') or raw.get('returns') or raw.get('hazard_contacts') or raw.get('plains',{}).get('player_damage'):return None
 frames=raw.get('frames',[]);goal=case.get('goal',[])
 if len(goal)!=4 or not frames or raw.get('ticks')!=len(frames):return None
 x,y,w,h=goal;streak=0;last=None
 for f in reversed(frames):
  v=f.get('real_velocity',[])
  if len(v)!=2 or not all(math.isfinite(t) for t in [f['x'],f['y'],*v]):break
  if not(x<=f['x']<=x+w and y<=f['y']<=y+h and f.get('grounded') and math.hypot(*v)<=1 and f.get('hp')==5 and not f.get('dead') and not f.get('returns') and not f.get('hazard_contacts') and f.get('air_exit_complete_frames')==0):break
  if last is not None and f['frame']!=last-1:break
  streak+=1;last=f['frame']
 required=max(6,int(case.get('settle_frames',6)))
 if streak<required:return None
 return dict(kind='review206_local_ROCK_terminal_observer_reanalysis',stableExit=True,
             consecutiveGroundedStationaryGoalFrames=streak,requiredFrames=required,
             originalRawOk=False,originalReason=raw['reason'],newPhysicsAttempts=0,
             explanation='AIR route terminal overwrote local ROCK stable streak; independently recomputed original grounded predicate from immutable frames')
