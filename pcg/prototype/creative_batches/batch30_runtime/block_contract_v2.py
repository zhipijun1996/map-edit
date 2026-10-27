"""Check original directed-route consumer fields before the original Engine.

No simulation or replacement schema: port_purpose consumes these keys during
final export. The v1 geometry checks and all original admission gates remain.
"""
import math
from .block_contract_v1 import inspect_sources as geometry_sources
from pcg.map_directed.library import fits


def inspect_sources(cases):
    response=geometry_sources(cases)
    for case,row in zip(cases,response['cases']):
        route=case.get('route_spec');ports={p['id']for p in case.get('ports',[])}
        errors=[]
        def reject(field,reason):errors.append(dict(field='route_spec.'+field,reason=reason))
        if not isinstance(route,dict):reject('','Original directed export requires an explicit route object')
        else:
            for key in ['id','role','from_port','to_port']:
                if not isinstance(route.get(key),str)or not route[key]:reject(key,'Explicit nonempty original route field required')
            for key in ['from_port','to_port']:
                if route.get(key)not in ports:reject(key,'Must bind an actual declared Port')
            if type(route.get('require_bell'))is not bool:reject('require_bell','Original three_port.port_purpose reads this explicit boolean; no inferred default')
            via=route.get('via_ports')
            if not isinstance(via,list)or any(not isinstance(p,str)or p not in ports for p in via):reject('via_ports','Original route consumer requires an explicit list of actual intermediate Ports')
        if errors:
            row['conflicts'].extend(errors);row['status']='needs_design'
        spec=case.get('map_specification');errors=[]
        def spec_reject(field,reason):errors.append(dict(field='map_specification.'+field,reason=reason))
        if not isinstance(spec,dict):spec_reject('','Resolved original Module demand object required; preserve the raw Map request separately')
        else:
            if spec.get('required_family')!=case.get('family'):spec_reject('required_family','Must bind the actual registered recipe')
            relations=spec.get('relations')
            if not isinstance(relations,list)or not relations or any(not isinstance(r,dict)or r.get('from_port')not in ports or r.get('to_port')not in ports for r in relations):
                spec_reject('relations','Original experiments.produce / WorkshopLibrary require explicit ordered relation objects, not an unresolved Map string')
            elif isinstance(route,dict)and not any((r['from_port'],r['to_port'])==(route.get('from_port'),route.get('to_port'))for r in relations):spec_reject('relations','The actual direction must appear in the resolved demand')
            if not isinstance(spec.get('ports'),dict)or spec['ports'].get('count')!=len(ports)or spec['ports'].get('required_normals')!=[p['normal']for p in case.get('ports',[])]:spec_reject('ports','Original lookup requires exact Port count and normals')
            space=spec.get('space',{})
            if not isinstance(space,dict)or any(type(space.get(k))not in [int,float]or not math.isfinite(space[k])or space[k]<=0 for k in ['max_width','max_height']):spec_reject('space','Resolved Module dimensions must be explicit positive max_width/max_height')
            elif 'max_port_span_x'in space and(type(space['max_port_span_x'])not in [int,float]or not math.isfinite(space['max_port_span_x'])or space['max_port_span_x']<0):spec_reject('space.max_port_span_x','An explicitly requested span must be finite and nonnegative')
            caps=spec.get('capabilities',{})
            if not isinstance(caps,dict)or not isinstance(caps.get('allOf'),list):spec_reject('capabilities.allOf','Original lookup requires explicit actual capabilities')
            # Scoped multi-route records do not call the legacy single-route
            # fits branch. Do not impose its optional span on valid old records.
            if not errors and 'max_port_span_x'in space:
                try:
                    if not fits(case,spec):spec_reject('','Original CandidateLibrary.fits rejects this resolved demand')
                except (KeyError,TypeError,ValueError)as error:spec_reject('',str(error))
        if errors:
            row['conflicts'].extend(errors);row['status']='needs_design'
    if any(row['status']!='requires_physics'for row in response['cases']):response['status']='needs_design'
    response['original_route_consumer']='pcg.prototype.plains.three_port.port_purpose; no physics executed'
    return response
