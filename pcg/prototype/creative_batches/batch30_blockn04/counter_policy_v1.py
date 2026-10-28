"""A paid external-air excursion is not an internal certified route."""
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification as original
from pcg.map_directed.block_grid.contracts import raster,EDGES
def classify(case,raw,check,outcome,baseline=None):
 result=original(case,raw,check,outcome,baseline)
 if not(result['invalidates_design']and check.get('reasons')==['actual_body_left_frozen_block_reservation']and outcome.get('ok')and baseline is not None and raw.get('shots',0)>baseline.get('shots',0)and check.get('causal',{}).get('real_gate_top_support')and raw.get('hp')==5 and not raw.get('returns')and not raw.get('plains',{}).get('player_damage')and not any(raw.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])):return result
 owned=set(map(tuple,case['block_grid']['cells']));outside=[];overruns={}
 for f in raw.get('frames',[]):
  body=[f['x']-12,f['y']-18,24,36];missing=raster(body)-owned
  if not missing:continue
  outside.append(dict(frame=f['frame'],body=body,unowned_cells=sorted(map(list,missing))))
  for k,p in case['block_ports'].items():
   dx,dy=EDGES[p['grid']['edge']];cell=p['grid']['cell']
   if(cell[0]+dx,cell[1]+dy)not in missing:continue
   distance=max(0,(f['x']-p['position'][0])*dx+12)if dx else max(0,(f['y']-p['position'][1])*dy+18)
   overruns[k]=max(overruns.get(k,0),distance)
 result.update(invalidates_design=False,reason='Extra paid shot still performs the actual opening/closing/same-gate top landing/refill; only external spatial coverage fails',scope='outside_contract_alternative',spatial_certification='UNKNOWN',certified_internal_alternative=False,nominal_body_qualification_unchanged=True,actual_unowned_body_frames=outside,maximum_outward_body_overrun_by_port_px=overruns,external_dependency='External air and neighbour availability are not certified; this is not an internal Module path guarantee.')
 return result
