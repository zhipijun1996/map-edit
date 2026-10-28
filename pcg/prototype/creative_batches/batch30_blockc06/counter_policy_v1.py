"""Separate a paid causal alternative from certification of its external air."""
from pcg.map_directed.block_grid.contracts import raster,EDGES
from pcg.prototype.creative_batches.batch30_runtime.produce_v1 import counter_classification as original_classification
from pcg.prototype.creative_batches.batch30_c06.rules_v2 import purpose as original_causal_purpose

def classify(case,raw,check,outcome,baseline=None):
 result=original_classification(case,raw,check,outcome,baseline)
 if not(result['invalidates_design']and check.get('reasons')==['actual_body_left_frozen_block_reservation']
        and case.get('rule_parameters',{}).get('route')=='low'and outcome.get('ok')and baseline is not None
        and raw.get('shots',0)>baseline.get('shots',0)and raw.get('hp')==5
        and not raw.get('plains',{}).get('player_damage')and not raw.get('returns')
        and not any(raw.get(k,0)for k in ['air_jumps','wall_jumps','grapples'])
        and original_causal_purpose(case,raw)['ok']):return result
 owned=set(map(tuple,case['block_grid']['cells']));size=case['block_grid']['size'];origin=case['block_grid']['origin'];outside=[];overruns={}
 for f in raw.get('frames',[]):
  body=[f['x']-12,f['y']-18,24,36];missing=raster(body,size,origin)-owned
  if not missing:continue
  outside.append(dict(frame=f['frame'],body=body,unowned_cells=sorted(map(list,missing))))
  for key,p in case['block_ports'].items():
   grid=p['grid'];dx,dy=EDGES[grid['edge']];cell=grid['cell'];outward=(cell[0]+dx,cell[1]+dy)
   if outward not in missing:continue
   distance=max(0,(f['x']-p['position'][0])*dx+12)if dx else max(0,(f['y']-p['position'][1])*dy+18)
   overruns[key]=max(overruns.get(key,0),distance)
 result.update(invalidates_design=False,
   reason='Paid low-route recoil preserves the causal choice; spatial-only scope failure is retained as external dependency, not a mechanism bypass',
   scope='outside_contract_alternative',spatial_certification='UNKNOWN',certified_internal_alternative=False,
   nominal_body_qualification_unchanged=True,actual_unowned_body_frames=outside,
   maximum_outward_body_overrun_by_port_px=overruns,
   external_dependency='The alternative uses air outside Module ownership. No wall, support or neighbour availability is inferred; it is not an internal path certificate.')
 return result
