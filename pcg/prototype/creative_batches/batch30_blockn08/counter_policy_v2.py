"""Original classification plus explicit slower external-air alternative scope."""
from pcg.map_directed.block_grid.contracts import raster,EDGES
from . import counter_policy_v1 as original,purpose_v1 as causal


def stable_A(case,raw):
 port=next(p for p in case['ports']if p['id']=='A');x,y=port['position'];streak=0
 for f in raw.get('frames',[]):
  match=f.get('grounded')and abs(f['x']-x)<=7 and abs(f['y']-y)<=1 and abs(f.get('vx',0))<=1
  streak=streak+1 if match else 0
  if streak>=12 and f.get('goal_stable_frames',0)>=12:return f
 return None


def classify(case,raw,check,outcome,baseline=None):
 result=original.classify(case,raw,check,outcome,baseline)
 if not(result['invalidates_design']and case.get('counterexample_kind')and case['route_spec']['from_port']=='B'and case['route_spec']['to_port']=='A'and check.get('reasons')==['actual_body_left_frozen_ownership']and outcome.get('ok')and baseline and baseline.get('ok')and causal.purpose(case,baseline)['ok']):return result
 ca=stable_A(case,raw);ba=stable_A(case,baseline);first=check.get('causal',{}).get('first_lower_support');lower=check.get('causal',{}).get('lower_support_frames',0)
 if not(ca and ba and first and lower>=12):return result
 landed=next((f for f in raw.get('frames',[])if f['frame']==first['frame']),None)
 if not(landed and landed.get('support_id')=='PairGateB_fold-pair'and landed.get('shot_charges')==1 and landed.get('jumps_used')==0 and landed.get('shot_cooldown',1)<=1e-9):return result
 safe=raw.get('hp')==5 and not raw.get('plains',{}).get('player_damage')and not raw.get('returns')and not any(raw.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
 resources=all(ca.get(k,0)>=ba.get(k,0)for k in ['shot_charges','energy','hp'])and ca.get('jumps_used',1)<=ba.get('jumps_used',0)and ca.get('shot_cooldown',1)<=ba.get('shot_cooldown',0)
 not_cheaper=raw.get('shots',0)>=baseline.get('shots',0)and raw.get('jumps',0)>=baseline.get('jumps',0)and ca['frame']>=ba['frame']
 paid=raw.get('shots',0)>baseline.get('shots',0)or raw.get('jumps',0)>baseline.get('jumps',0)or ca['frame']>ba['frame']
 if not(safe and resources and not_cheaper and paid):return result
 # Same read-only reservation/overrun audit as existing C06/N04 policies.
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
 result.update(invalidates_design=False,reason='Slower external-air excursion retains actual lowerbridge catch/refill and fulloriginalgoals/resources; it is outside the Modulecontract, not a cheaper internal solution.',scope='outside_contract_alternative',accepted_module_solution=False,certified_internal_alternative=False,spatial_certification='UNKNOWN',Map_space_dependency='UNKNOWN',nominal_body_qualification_unchanged=True,actual_unowned_body_frames=outside,actual_unowned_body_frame_count=len(outside),actual_unowned_body_sweep_frames=sweeps,maximum_outward_body_overrun_by_port_px=overruns,actual_twelve_frame_A_stability=dict(nominal=ba['frame'],alternative=ca['frame'],delta=ca['frame']-ba['frame']),external_dependency='Airoutsideownedcells andnonportreentryareUNKNOWN. No support, neighbour, wall, Mapboundary or internal solution evidence inferred.')
 return result
