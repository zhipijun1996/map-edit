"""Read-only terminal observation when the explicit TOP neighbor catches ascent first."""
import math
from .revision058_boundary_v1 import VERSIONS

def observe(case,raw):
 s=case.get('approved_implementation',{});p=case.get('migration_probe',{})
 if VERSIONS.get(s.get('reviewId'))!=s.get('designVersion')or not(s.get('reviewId','').startswith('idea-31639')or s.get('reviewId')=='idea-interface-s07-001'):return None
 if p.get('kind')not in ['local_boundary','continuous_exit']or p.get('direction')!='egress'or p.get('normal')!=[0,-1]:return None
 if p.get('kind')=='local_boundary'and not p.get('revision058Top',{}).get('wholeCanonicalTransit'):return None
 n=p.get('neighbor',{});floor=n.get('floor',[]);x=p.get('boundary',[None,None])[0]
 if floor!=[x-48,-32,96,12]or n.get('source')!='explicit_test_neighbor'or n.get('copiedIntoModule')is not False:return None
 if raw.get('ok')or not str(raw.get('plan_error','')).startswith('trigger_timeout/')or not raw.get('module_definition_valid'):return None
 if raw.get('hp')!=5 or raw.get('dead')or raw.get('returns')or raw.get('damage_commits')or raw.get('hazard_contacts')or raw.get('plains',{}).get('player_damage'):return None
 goal=case.get('goal',[])
 if goal!=[x-9,-55,18,10]:return None
 error=raw['plan_error'].split('/')
 try:command=case['control_plan'][int(error[1])]
 except (ValueError,IndexError,KeyError):return None
 waiting=command.get('trigger',{}).get('migration_goal',[])
 if len(waiting)!=4 or not(waiting[0]<=x<=waiting[0]+waiting[2]and waiting[1]<=14<=waiting[1]+waiting[3]):return None
 frames=raw.get('frames',[]);count=0;last=None
 if not frames or len(frames)!=raw.get('ticks'):return None
 for f in reversed(frames):
  v=f.get('real_velocity',[])
  if len(v)!=2 or not all(math.isfinite(t)for t in [f['x'],f['y'],*v]):break
  if not(abs(f['x']-x)<=4 and abs(f['y']+50)<=.05 and f.get('grounded')and math.hypot(*v)<=1 and f.get('hp')==5 and not f.get('returns')and not f.get('dead')and not f.get('hazard_contacts')):break
  if last is not None and f['frame']!=last-1:break
  count+=1;last=f['frame']
 required=max(24,int(case.get('settle_frames',6)))
 if count<required:return None
 return dict(stableExit=True,kind='revision058_explicit_TOP_neighbor_caught_canonical_ascent',consecutiveGroundedStationaryGoalFrames=count,requiredFrames=required,originalRawOk=False,newPhysicsAttempts=0,newIndependentHoldout=False,rawUnchanged=True,explanation='Native adjacent one-way deck catches the ascent at -50 before the intermediate internal14 wait. Full-body crossing, aperture, order, health and world-outcome gates remain mandatory.')
