"""Fail-closed structural screens, not an aesthetic or human fun score."""
from collections import Counter
from ..block_grid.contracts import placed_cells

def screen(graph,modules):
    by={m['id']:m for m in modules};errors=[]
    if set(by)!={n['id']for n in graph['nodes']}:return dict(ok=False,errors=['blueprint_node_mismatch'])
    actual_pairs={(e['id'],e['from'],e['to'])for e in graph['edges']}
    route_samples=[]
    for route in graph['principal_routes']:
        flat=longest=0;deltas=[]
        for key in route['nodes'][1:-1]:
            m=by[key];required=[e for e in graph['edges']if key in[e['from'],e['to']]and e['purpose']==route['id']+'_main']
            ps=[m['ports'][e['id']]['position']for e in required]
            dy=ps[1][1]-ps[0][1];deltas.append(dy);flat=flat+1 if abs(dy)<128 else 0;longest=max(longest,flat)
        if longest>1:errors.append('repeated_horizontal_band/'+route['id'])
        if not any(abs(d)>=256 for d in deltas):errors.append('route_lacks_meaningful_elevation/'+route['id'])
        route_samples.append(dict(id=route['id'],internal_port_height_changes=deltas,longest_horizontal_chain=longest))
    counts=Counter(m['selection_family'].split('-640')[0].split('-768')[0]for m in modules)
    if max(counts.values())>2:errors.append('repeated_macro_family')
    junctions=[by[n['id']]['selection_family']for n in graph['nodes']if n['role']=='junction']
    if len(junctions)!=len(set(junctions)):errors.append('repeated_junction_shape')
    cells=set().union(*(placed_cells(m,m['spec']['placement'])for m in modules));xs=[p[0]for p in cells];ys=[p[1]for p in cells]
    box=(max(xs)-min(xs)+1)*(max(ys)-min(ys)+1);fill=len(cells)/box
    if fill<.20:errors.append('excessive_unreserved_blank_space')
    # Compactness is only a selection preference among accepted candidates.
    return dict(ok=not errors,errors=errors,reserved_block_fill=fill,box_blocks=box,principal_routes=route_samples,
        junction_families=junctions,score=round(box+50*(1-fill),4),scope='Static design screens only; actual routes, challenge necessity, readability and fun need separate evidence')
