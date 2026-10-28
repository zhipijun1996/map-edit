"""Independent calibrated observation; old failures never overwritten."""
import copy,json,math
from pathlib import Path
from . import cell_probe_v1 as source
from pcg.prototype.workshop.engine import ROOT,WorkshopEngine
from pcg.prototype.workshop.experiments import write
HERE=Path(__file__).parent

def cases():
 cs=source.cases()
 for c in cs:c['id']=c['id'].replace('cell-v1','cell-v2')
 # Same tangent/speed, translated to the exact old loop pre-pause deck pose.
 a,b=source.POINTS[8:10];length=sum(math.dist(x,y)for x,y in zip(source.POINTS,source.POINTS[1:]));speed=length/8;v=[(b[j]-a[j])/math.dist(a,b)*speed for j in range(2)];at119=source.sample(source.POINTS,2.05/8+.25);start=[at119[j]-v[j]*(2.05-.2)for j in range(2)];finish=[start[j]+v[j]*3.8 for j in range(2)]
 c=copy.deepcopy(cs[0]);c.update(id='b31-n25-original-diagonal-pause-control-v2',spawn=[start[0],start[1]-30],max_frames=300,cell_pause_probe=True,test_kind='original_diagonal_control');c['moving_platforms']=[dict(platform_id='base-diagonal',start=start,finish=finish,size=[160,24],travel_duration=3.8,dwell_duration=.2,initial_phase=0)];cs.append(c)
 return cs

def baseline_point(raw,t):
 elapsed=(t+raw.get('initial_phase',0)*8)%8;dwell=raw['dwell_duration'];travel=raw['travel_duration']
 if elapsed<dwell:f=0
 elif elapsed<dwell+travel:f=(elapsed-dwell)/travel
 elif elapsed<2*dwell+travel:f=1
 else:f=1-(elapsed-2*dwell-travel)/travel
 return[raw['start'][j]+(raw['finish'][j]-raw['start'][j])*f for j in range(2)]

def calibrated(c,r):
 fs=r.get('frames',[]);raw=c['moving_platforms'][0];loop=raw.get('trajectory_kind')=='closed_polyline_loop/v1';old=source.check(c,r)if loop else None;why=[]
 if old:why += [s for s in old['reasons']if s not in ['actual_position_differs_from_closed_JS_arc_length_path','actual_loop_pose_discontinuity']]
 pauses=r.get('n25',{}).get('pause_receipts',[]);resume=[]
 for p in pauses:
  first=next((f for f in fs if f['module_clock']>p['before']['clock']+1e-8),None)
  if first:resume.append(first['frame'])
  if not p['unchanged']:why.append('native_pause_clock_actor_deck_not_frozen')
 speed=sum(math.dist(a,b)for a,b in zip(source.POINTS,source.POINTS[1:]))/raw['loop_period']if loop else math.dist(raw['start'],raw['finish'])/raw['travel_duration']
 target_error=0.;node_error=0.;non_native_spikes=[];last=None;last_sample=None;server_errors=[0.,0.,0.];transition=[]
 for f in fs:
  s=f.get('n25_calibration',{}).get('movers',[])
  if len(s)!=1:why.append('missing_readonly_calibrated_mover');continue
  p=s[0];clock=f['module_clock'];lag=2 if f['frame']in resume else 1;readtime=clock-lag/60
  expected=source.sample(source.POINTS,clock/raw['loop_period']+raw['initial_phase'])if loop else baseline_point(raw,clock)
  prior=source.sample(source.POINTS,readtime/raw['loop_period']+raw['initial_phase'])if loop else baseline_point(raw,readtime)
  target_error=max(target_error,math.dist(p['definition_target'],expected));node_error=max(node_error,math.dist(p['node_pose'],prior))
  for i in range(3):server_errors[i]=max(server_errors[i],math.dist(p['physics_server_pose'],p[['definition_target','previous_tick_target','two_tick_target'][i]]))
  if last is not None:
   step=math.dist(last,p['node_pose']);budget=speed*max(0,readtime-last_sample)+.1
   if step>budget:non_native_spikes.append(dict(frame=f['frame'],actual_step=step,expected_native_readback_elapsed=readtime-last_sample,bound=budget))
  last=p['node_pose'];last_sample=readtime
  if any(abs(f['frame']-index)<=2 for index in resume):
   transition.append(dict(frame=f['frame'],clock=clock,readback_clock=readtime,node=p['node_pose'],physics_server=p['physics_server_pose'],actor=[f['x'],f['y']],grounded=f['grounded'],support=f['support_id'],fullbody_horizontal_margin=68-abs(f['x']-p['node_pose'][0]),hp=f['hp'],energy=f['energy'],shot_charges=f['shot_charges'],jumps_used=f['jumps_used'],cooldown=f['shot_cooldown']))
 if target_error>.002:why.append('same_clock_definition_vs_JS_error_above_original_.002')
 if node_error>.002:why.append('original_native_readback_sequence_error_above_.002')
 if non_native_spikes:why.append('displacement_exceeds_actual_native_readback_elapsed_bound')
 if c.get('cell_pause_probe'):
  if len(resume)!=1:why.append('actual_pause_transition_missing')
  if any(f['hp']!=5 or f['energy']!=100 or f['shot_charges']!=1 or f['jumps_used']!=0 or f['cooldown']!=0 or f['fullbody_horizontal_margin']<8 for f in transition):why.append('pause_transition_resources_or_body_margin_failed')
  if not any(f['frame']==resume[0]+1 and f['grounded']for f in transition):why.append('measured_phase_no_actual_one_tick_recatch')
 return dict(calibration_scope_ok=not why,reasons=sorted(set(why)),old_original_check=old,new_pose_tolerance_unchanged=.002,same_clock_definition_vs_JS_max_error=target_error,node_vs_declared_native_readback_max_error=node_error,unexpected_displacement_spikes=non_native_spikes,physics_server_error_vs_clock_lags_0_1_2=server_errors,actual_pause_transition=transition,pause_worldtick_single_step_continuity='UNSUPPORTED'if pauses else'not_paused_in_this_case',arbitrary_pause_phase_transfer='UNKNOWN',original_physics_or_controls_changed=False)

def main():
 e=WorkshopEngine(ROOT/'results/workshop-batch30-blockn25-cell-calibration-v2',extra_sources=[Path(__file__),Path(source.__file__),HERE/'calibration-v2.json',HERE/'measure_v2.gd',HERE/'runner_v2.gd',*source.SOURCE_DEPENDENCIES],runner_script=HERE/'runner_v2.gd');rows=[]
 for c,r,ev in e.run(cases(),'fresh-eight-plus-matched-original-diagonal'):
  row=dict(id=c['id'],calibration=calibrated(c,r),evidence=ev);rows.append(row);print(json.dumps(row),flush=True)
 write(e.out/'receipt.json',dict(actual_cases=e.sim.cases,rows=rows,calibration_scope_passed=sum(x['calibration']['calibration_scope_ok']for x in rows),new_modules=0,new_families=0,prior8_rejections_preserved=True,arbitrary_pause_and_single_worldtick_continuity='UNKNOWN_UNSUPPORTED'))
if __name__=='__main__':main()
