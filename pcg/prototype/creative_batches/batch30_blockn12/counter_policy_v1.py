"""Original classifier plus slower external-air reward-rejoin scope only."""
import math
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification as original,external_outcome
from pcg.prototype.workshop.evaluate import purpose as original_causal
from pcg.map_directed.block_grid.contracts import raster,EDGES
from . import rules_v1 as source

def stable_goal(case,raw):
 x,y=case['exit_port'];required=max(6,int(case.get('settle_frames',6)));streak=0
 for f in raw.get('frames',[]):
  v=f.get('real_velocity',[f.get('vx',0),f.get('vy',0)])
  match=f.get('grounded')and abs(f['x']-x)<=7 and abs(f['y']-y)<=1 and math.hypot(*v)<=1
  streak=streak+1 if match else 0
  if streak>=required and f.get('goal_stable_frames',0)>=required:return f
 return None

def classify(case,raw,check,outcome,baseline=None):
 result=original(case,raw,check,outcome,baseline)
 if not(result['invalidates_design']and case.get('counterexample_kind')and case.get('route_spec',{}).get('to_port')=='C'and check.get('reasons')==['actual_body_left_frozen_Block_ownership']and outcome.get('ok')and baseline and baseline.get('ok')and source.purpose(case,baseline)['ok']and external_outcome(case,baseline)['ok']and original_causal(case,raw)['ok']):return result
 ca=stable_goal(case,raw);ba=stable_goal(case,baseline)
 if not(ca and ba):return result
 safety=raw.get('hp')==5 and not raw.get('returns')and not raw.get('plains',{}).get('player_damage')and not any(raw.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
 resources=all(ca.get(k,0)>=ba.get(k,0)for k in ['shot_charges','energy','hp'])and ca.get('jumps_used',1)<=ba.get('jumps_used',0)and ca.get('shot_cooldown',1)<=ba.get('shot_cooldown',0)
 not_cheaper=raw.get('shots',0)>=baseline.get('shots',0)and raw.get('jumps',0)>=baseline.get('jumps',0)and ca['frame']>=ba['frame']
 paid=raw.get('shots',0)>baseline.get('shots',0)or raw.get('jumps',0)>baseline.get('jumps',0)or ca['frame']>ba['frame']
 claims=[e for e in raw.get('workshop',{}).get('events',[])if e.get('type')=='chest_claim'and e.get('accepted')and e.get('id')=='upper-cache'and e.get('amount',0)>=12]
 support=next((f for f in raw.get('frames',[])if claims and f.get('grounded')and f.get('support_id')=='Platform1'and f.get('shot_charges')==1 and f.get('jumps_used')==0 and f.get('shot_cooldown',1)<=1e-9 and f['frame']<=claims[0]['frame']),None)
 if not(safety and resources and not_cheaper and paid and len(claims)==1 and support):return result
 owned=set(map(tuple,case['block_grid']['cells']));size=case['block_grid']['size'];origin=case['block_grid']['origin'];outside=[];overruns={};sweeps=[];fs=raw.get('frames',[])
 for f in fs:
  body=[f['x']-12,f['y']-18,24,36];missing=raster(body,size,origin)-owned
  if not missing:continue
  outside.append(dict(frame=f['frame'],body=body,unowned_cells=sorted(map(list,missing))))
  for key,p in case['block_ports'].items():
   grid=p['grid'];dx,dy=EDGES[grid['edge']];cell=grid['cell']
   if(cell[0]+dx,cell[1]+dy)not in missing:continue
   distance=max(0,(f['x']-p['position'][0])*dx+12)if dx else max(0,(f['y']-p['position'][1])*dy+18)
   overruns[key]=max(overruns.get(key,0),distance)
 for a,b in zip(fs,fs[1:]):
  if not raster([min(a['x'],b['x'])-12,min(a['y'],b['y'])-18,abs(a['x']-b['x'])+24,abs(a['y']-b['y'])+36],size,origin)<=owned:sweeps.append(b['frame'])
 result.update(invalidates_design=False,reason='Slower same-C reward-rejoin uses original one-shot investment and real B refill/cache, with an external-air dependency; it is not an internal Module solution.',scope='outside_contract_alternative',accepted_module_solution=False,certified_internal_alternative=False,spatial_certification='UNKNOWN',Map_space_dependency='UNKNOWN',nominal_body_qualification_unchanged=True,actual_unowned_body_frames=outside,actual_unowned_body_frame_count=len(outside),actual_unowned_body_sweep_frames=sweeps,maximum_outward_body_overrun_by_port_px=overruns,actual_original_stable_C=dict(required_frames=max(6,int(case.get('settle_frames',6))),nominal=ba['frame'],alternative=ca['frame'],delta=ca['frame']-ba['frame']),actual_upper_reward_claim=claims[0],actual_upper_support_refill={k:support.get(k)for k in ['frame','support_id','shot_charges','jumps_used','shot_cooldown']},external_dependency='Unowned outward air/nonport reentry UNKNOWN. No B->C certificate, neighbour/wall/Map assumption, ownership expansion or generic rejoin qualification.')
 return result
