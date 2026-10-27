"""Exact matching for existing OFFLINE recipe specifications, not Map planning.

No layout, graph, runtime state search or universal Module rules live here.
"""
from copy import deepcopy
from pcg.prototype.factory.core.quality import digest

def rect_bounds(case):
    rs=case['platforms'][:]+case.get('hazards',[])[:]
    for saw in case.get('saws',[]):
        x,y=saw['origin'];dx,dy=map(abs,saw['travel']);r=saw['radius']
        rs.append([x-dx-r,y-dy-r,2*(dx+r),2*(dy+r)])
    for latch in case.get('latches',[]):rs.append(latch['gate'])
    return [min(r[0] for r in rs),min(r[1] for r in rs),
        max(r[0]+r[2] for r in rs)-min(r[0] for r in rs),max(r[1]+r[3] for r in rs)-min(r[1] for r in rs)]

def fits(case,spec):
    bounds=rect_bounds(case)
    return (case['family']==spec['required_family'] and (len(case['ports']) if case.get('ports') else 2)==spec['ports']['count']
        and abs(case['entry_port'][1]-case['exit_port'][1]-spec.get('rise',case['entry_port'][1]-case['exit_port'][1]))<1e-6
        and bounds[2]<=spec['space']['max_width'] and bounds[3]<=spec['space']['max_height']
        and abs(case['exit_port'][0]-case['entry_port'][0])<=spec['space']['max_port_span_x']
        and case['entry_port'][1]==spec.get('entry_y',case['entry_port'][1])
        and set(case['capabilities'])<=set(spec['capabilities']['allOf']))

def demand_key(spec):
    # IDs, prose labels and seed metadata are not gameplay constraints. The
    # present adapter deliberately retains local port IDs and geometry: it must
    # not pretend to support arbitrary relabeling, mirroring or resizing.
    value=deepcopy(spec)
    for key in ['id','map_seed','objective','revision','mechanic_requirements','budget']:value.pop(key,None)
    if 'node'in value:value['node'].pop('label',None)
    if 'design_contract'in value:
        value['design_contract'].pop('hypothesis_sha256',None)
    return digest(value)
