#!/usr/bin/env python3
"""R2 region-network direction prototype. No authored start-to-boss spine.

A constrained planar proximity network is grown around spatial responsibilities;
mission roles and dedicated expeditions are bound before mask/port embedding.
This changes the topology model, not merely the direction of a fixed chain.
The old A/B/C experiment and its evidence are intentionally left unchanged.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict, deque
import copy
import heapq
import json
import math
from pathlib import Path
import statistics
import time
import mapgen as base

VERSION = 'map-notes/region-network-v2'
REGIONS = {
    'plains': {'radii': [49, 34], 'abilities': ['jump', 'shot_recoil'],
               'landmarks': ['风车高地', '溪谷营地', '旧钟庭院'], 'intent': 'open courts, creek detours, upper reward expedition'},
    'forest': {'radii': [37, 48], 'abilities': ['jump', 'shot_recoil', 'grapple'],
               'landmarks': ['中空巨木', '根下休息处', '外冠观望台'], 'intent': 'inner trunk and outer crown routes, distinct climb and descent returns'},
}


def orient(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])


def triangulate(points):
    """Incremental Delaunay edges, not a tile-neighbor grid."""
    count = len(points)
    span = max(max(abs(x), abs(y)) for x, y in points) * 16 + 128
    all_points = points + [(-span, -span), (span, -span), (0, span)]
    triangles = [(count, count+1, count+2)]
    def inside(triangle, p):
        a, b, c = [all_points[v] for v in triangle]
        ax, ay = a[0]-p[0], a[1]-p[1]
        bx, by = b[0]-p[0], b[1]-p[1]
        cx, cy = c[0]-p[0], c[1]-p[1]
        determinant = ((ax*ax+ay*ay)*(bx*cy-by*cx)
                       -(bx*bx+by*by)*(ax*cy-ay*cx)+(cx*cx+cy*cy)*(ax*by-ay*bx))
        return determinant * (1 if orient(a, b, c) > 0 else -1) > 0.0001
    for i, point in enumerate(points):
        bad = [triangle for triangle in triangles if inside(triangle, point)]
        edges = Counter(tuple(sorted(edge)) for a, b, c in bad for edge in [(a,b),(b,c),(c,a)])
        triangles = [t for t in triangles if t not in bad]
        triangles.extend((a,b,i) for (a,b), n in sorted(edges.items()) if n == 1 and orient(all_points[a],all_points[b],point))
    return sorted({tuple(sorted(edge)) for a,b,c in triangles if max(a,b,c) < count for edge in [(a,b),(b,c),(c,a)]})


def neighbors(nodes, edges):
    out = {n: set() for n in nodes}
    for a,b in edges:
        out[a].add(b); out[b].add(a)
    return out


def components(nodes, edges, excluded=None):
    ids = set(nodes) - ({excluded} if excluded is not None else set())
    if not ids: return []
    adj = neighbors(nodes, edges); result = []
    while ids:
        group = {min(ids)}; queue = deque(group); ids -= group
        while queue:
            for other in adj[queue.popleft()] & ids:
                group.add(other); queue.append(other); ids.remove(other)
        result.append(group)
    return result


def articulation_nodes(nodes, edges):
    # Small graphs; explicit deletion is transparent and independently testable.
    return [n for n in nodes if len(components(nodes, edges, n)) > 1]


def shortest_path(g, source, target, blocked_edges=frozenset(), initial_only=True, core_only=False):
    adj = base.expand_arcs(g, blocked_edges)
    queue = [(0., (source,))]; best = {source: 0.}
    while queue:
        cost, path = heapq.heappop(queue)
        if cost != best[path[-1]]: continue
        if path[-1] == target: return cost, list(path)
        for other, edge in adj[path[-1]]:
            if core_only and edge['purpose'] != 'regional_route': continue
            if initial_only and (edge['switch'] or not set(edge['requires']) <= set(g['initial_abilities'])): continue
            new = cost + edge['cost']
            if new < best.get(other, math.inf):
                best[other] = new; heapq.heappush(queue, (new, path + (other,)))
    return math.inf, []


def sampled_points(rng, region, count=20):
    if not 12 <= count <= 48: raise ValueError('regional_core_count_outside_12_48_budget')
    rx, ry = REGIONS[region]['radii']; points = []
    if count != 20:
        factor = math.sqrt(count/20)
        rx, ry = math.ceil(rx*factor), math.ceil(ry*factor)
    for _ in range(6000):
        x = rng.next_int(2*rx+1)-rx; y = rng.next_int(2*ry+1)-ry
        if (x/rx)**2+(y/ry)**2 > 1: continue
        if any((x-a)**2+(y-b)**2 < 13**2 for a,b in points): continue
        points.append((x,y))
        if len(points) == count: return points
    raise ValueError('point_sampling_budget_exhausted')


def hull_indices(points):
    ordered = sorted(range(len(points)), key=lambda i: points[i])
    def half(order):
        hull = []
        for i in order:
            while len(hull)>1 and orient(points[hull[-2]],points[hull[-1]],points[i]) <= 0: hull.pop()
            hull.append(i)
        return hull
    return half(ordered)[:-1]+half(ordered[::-1])[:-1]


def core_network(seed, region, core_count=20):
    rng = base.RandomStream(seed, 'regional-core', version=VERSION)
    points = sampled_points(rng, region, core_count); ids = list(range(len(points)))
    edges = triangulate(points)
    if len(components(ids, edges)) != 1 or articulation_nodes(ids, edges):
        raise ValueError('initial_proximity_network_not_biconnected')
    # Remove edges only if a room cannot become a regional bottleneck. This is
    # not a spanning tree followed by ornamental leaf rewards.
    target_edges = round(core_count*1.3) + rng.next_int(3)
    ordered = sorted(rng.shuffle(edges), key=lambda e: -math.dist(points[e[0]], points[e[1]]))
    for edge in ordered:
        if len(edges) <= target_edges: break
        trial = [e for e in edges if e != edge]
        adj = neighbors(ids, trial)
        if any(len(v)<2 for v in adj.values()) or articulation_nodes(ids, trial): continue
        edges = trial
    return rng, points, edges


def construct(seed, region, core_count=20):
    rng, points, pairs = core_network(seed, region, core_count)
    g = {'entry': '', 'goal': 'boss', 'initial_abilities': REGIONS[region]['abilities'][:],
         'nodes': [], 'edges': [], 'branches': [], 'rewrite_log': [], 'core_nodes': [f'r{i}' for i in range(len(points))]}
    for i, point in enumerate(points):
        g['nodes'].append({'id': f'r{i}', 'role': 'hub', 'label': f'场所 {i}', 'ideal': list(point),
                           'grants': [], 'opens': [], 'reward': 0, 'risk': 1, 'intent': 'regional-route-choice'})
    for a,b in pairs:
        # Route length is an uncalibrated module-slot estimate, not play time.
        cost = round(0.6 + math.dist(points[a], points[b])/17, 3)
        base.add_edge(g, f'r{a}', f'r{b}', cost=cost, purpose='regional_route')
    hull = hull_indices(points); candidates = []
    yspan = max(y for x,y in points)-min(y for x,y in points)
    for entry in hull:
        for prep in hull:
            if entry == prep: continue
            cost, path = shortest_path(g, f'r{entry}', f'r{prep}')
            centers = [points[int(n[1:])] for n in path]
            if 4 <= len(path)-1 <= 8 and abs(points[entry][1]-points[prep][1]) >= yspan*.35:
                candidates.append((entry,prep,path,cost))
    if not candidates: raise ValueError('no_compact_multilevel_entry_prep_pair')
    entry, prep, path, cost = rng.choice(candidates)
    g['entry'] = f'r{entry}'; prep_id = f'r{prep}'
    byid = {n['id']: n for n in g['nodes']}
    byid[g['entry']].update(role='start', label='区域入口', intent='read two first-visit directions')
    byid[prep_id].update(role='prep', label='Boss 前庭', opens=['boss_access'])
    # Boss sits outside its chosen perimeter forecourt, with an explicit last
    # door; the whole region does not acquire a single mandatory room chain.
    px,py = points[prep]; norm = math.hypot(px,py) or 1
    boss_point = [round(px+px/norm*18), round(py+py/norm*18)]
    if any(math.dist(boss_point,p)<11 for p in points): raise ValueError('boss_room_clearance')
    g['nodes'].append({'id': 'boss', 'role': 'boss', 'label': 'Boss', 'ideal': boss_point,
                       'grants': [], 'opens': [], 'reward': 0, 'risk': 2, 'intent': 'region culmination'})
    base.add_edge(g,prep_id,'boss',switch='boss_access',cost=1.2,purpose='boss_gate')
    # Actual semantic landmarks on separated core rooms, not a decorative list.
    degrees = neighbors(list(range(len(points))), pairs)
    landmarks = []
    choices = sorted((i for i in range(len(points)) if i not in [entry,prep]), key=lambda i: (-len(degrees[i]),i))
    for title in REGIONS[region]['landmarks']:
        pick = next((i for i in choices if all(math.dist(points[i],points[j])>=24 for j in landmarks)), choices[0])
        landmarks.append(pick); choices.remove(pick)
        byid[f'r{pick}'].update(label=title, intent='recognizable junction and recoverable route meeting')
    byid[f'r{landmarks[1]}']['role'] = 'rest'
    byid[f'r{landmarks[2]}']['opens'] = ['hidden_route_known']
    g['landmarks'] = [f'r{i}' for i in landmarks]
    # Deep expeditions occupy perimeter ears. They have distinct entry/rejoin,
    # long challenge arms and discovery-opened return edges. The core remains.
    available = [(hull[i], hull[(i+1)%len(hull)]) for i in range(len(hull)) if entry not in [hull[i],hull[(i+1)%len(hull)]] and prep not in [hull[i],hull[(i+1)%len(hull)]]]
    occupied = [tuple(n['ideal']) for n in g['nodes']]
    for bi in range(2):
        fitted = None
        for a,b in rng.shuffle(available):
            ax,ay = points[a]; bx,by = points[b]; dx,dy = bx-ax,by-ay; length=math.hypot(dx,dy)
            nx,ny = dy/length,-dx/length  # CCW hull's outside.
            for chain_count in rng.shuffle([3,4,5]):
                for depth in [23,35,48,64]:
                    curve=[]
                    for j in range(chain_count):
                        t=(j+1)/(chain_count+1); bulge=math.sin(math.pi*t)*depth
                        curve.append((round(ax+t*dx+nx*bulge),round(ay+t*dy+ny*bulge)))
                    if any(math.dist(c,p)<11 for c in curve for p in occupied): continue
                    if any(math.dist(c,p)<9 for i,c in enumerate(curve) for p in curve[i+1:]): continue
                    fitted=(a,b,curve);break
                if fitted: break
            if fitted:break
        if fitted is None: raise ValueError('reward_expedition_spatial_budget')
        a,b,curve=fitted; available.remove((a,b)); chain=[]; flag=f'expedition_return_{bi}'
        for j,point in enumerate(curve):
            nid=f'exp{bi}_{j}'; last=j==len(curve)-1; chain.append(nid)
            g['nodes'].append({'id':nid,'role':'reward' if last else 'challenge',
                'label': ('隐蔽奖励' if bi else '深处奖励') if last else f'进阶挑战 {bi+1}.{j+1}',
                'ideal':list(point),'grants':[],'opens':[flag] if last else [],'reward':[18,30][bi] if last else 0,
                'risk':2+bi,'intent':'optional expedition, distinct rejoin and earned fast return'})
        route=[f'r{a}']+chain+[f'r{b}']
        for j,(u,v) in enumerate(zip(route,route[1:])):
            base.add_edge(g,u,v,purpose='hidden_route' if bi and j==0 else 'reward_challenge',
                          switch='hidden_route_known' if bi and j==0 else None,
                          requires=['grapple' if region=='forest' else 'shot_recoil'] if j==0 else [],
                          cost=2+bi*.4,bidirectional=not (j==len(route)-2))
        base.add_edge(g,chain[-1],f'r{a}',purpose='return_shortcut',switch=flag,cost=.7,bidirectional=False)
        g['branches'].append({'id':f'expedition_{bi}','nodes':chain,'entry':f'r{a}','rejoin':f'r{b}','reward':chain[-1]})
        occupied.extend(curve)
    g['mission_policy']={'entry':g['entry'],'boss_forecourt':prep_id,'goal':'boss',
        'main_route':'not_authored; shortest routes measured after regional network generation',
        'core_return':'biconnected before optional state gates','region_intent':REGIONS[region]['intent'],
        'prototype_scope':'abstract spaces only; landmark visibility and restorative content not rendered gameplay'}
    g['rewrite_log']=[{'rule':'prune_planar_proximity_while_preserving_two_connected_region','core_nodes':len(points),'core_edges':len(pairs)},
                      {'rule':'bind_spatially_separated_entry_landmarks_boss_forecourt_then_perimeter_expeditions'}]
    return g


def approach_routes(g):
    prep = g['mission_policy']['boss_forecourt']; cost, first=shortest_path(g,g['entry'],prep,core_only=True)
    if not first:return []
    edges = {frozenset([e['from'],e['to']]):e['id'] for e in g['edges'] if e['purpose']=='regional_route'}
    first_pairs={frozenset(p) for p in zip(first,first[1:])}; alternatives=[]
    for pair in sorted(first_pairs,key=lambda p:sorted(p)):
        edge = edges[pair]; alt_cost,alt=shortest_path(g,g['entry'],prep,frozenset([edge]),core_only=True)
        if not alt:continue
        alt_pairs={frozenset(p) for p in zip(alt,alt[1:])}
        similarity=len(first_pairs&alt_pairs)/len(first_pairs|alt_pairs)
        alternatives.append((similarity,alt_cost,alt))
    if not alternatives:return [{'nodes':first,'cost':cost}]
    similarity,other_cost,other=min(alternatives)
    return [{'nodes':first,'cost':round(cost,3)}, {'nodes':other,'cost':round(other_cost,3),'edge_jaccard_with_fast':round(similarity,3)}]


def diagnostics(g):
    core=g['core_nodes']; pairs=[(e['from'],e['to']) for e in g['edges'] if e['purpose']=='regional_route']
    routes=approach_routes(g); node={n['id']:n for n in g['nodes']}
    centers=[node[n]['ideal'] for n in routes[0]['nodes']] if routes else []
    horizontal_span=max((p[0] for p in centers),default=0)-min((p[0] for p in centers),default=0)
    vertical_span=max((p[1] for p in centers),default=0)-min((p[1] for p in centers),default=0)
    return {'core_articulation_nodes':articulation_nodes(core,pairs),'first_visit_routes_to_forecourt':routes,
            'fast_route_cost_before_boss':routes[0]['cost'] if routes else None,
            'fast_route_room_y_span':vertical_span,'fast_route_room_x_span':horizontal_span,
            'landmarks':g['landmarks'],
            'route_measure_scope':'initial abilities and no pre-opened shortcut; two sample routes, not all possible routes',
            'design_quality':'unverified; constraints express requested direction, not a fun certificate'}


def validate_region_intent(g):
    """Falsifiable direction checks. They cannot certify Hollow-Knight-like fun."""
    errors=[]; core=g.get('core_nodes',[])
    pairs=[(e['from'],e['to']) for e in g['edges'] if e['purpose']=='regional_route']
    if len(core)<12: return ['regional_core_too_small']
    if any(a not in core or b not in core for a,b in pairs): return ['invalid_core_edge']
    if len(components(core,pairs))!=1: return ['regional_core_disconnected']
    if articulation_nodes(core,pairs): errors.append('mandatory_core_chain_or_bottleneck')
    info=diagnostics(g);routes=info['first_visit_routes_to_forecourt']
    if len(routes)<2 or routes[0]['nodes']==routes[1]['nodes']: errors.append('missing_initial_route_choice')
    if len(routes)>=2 and routes[1]['edge_jaccard_with_fast']>.5: errors.append('alternatives_overlap_too_much')
    if info['fast_route_room_y_span']<18: errors.append('horizontal_only_fast_route')
    # Gates at the final Boss room are allowed, but exploration before it must
    # not be a mandatory room chain with rewards attached to its sides.
    for branch in g['branches']:
        if branch['entry']==branch['rejoin']:errors.append('expedition_returns_through_same_only_entrance')
        shortcuts=[e for e in g['edges'] if e['from']==branch['reward'] and e['purpose']=='return_shortcut']
        if not shortcuts: errors.append('missing_earned_return')
        for edge in shortcuts:
            openers={n['id'] for n in g['nodes'] if edge['switch'] in n['opens']}
            if not edge['switch'] or openers!={branch['reward']}:errors.append('shortcut_not_earned_at_reward')
    return sorted(set(errors))


def generate(seed,region,embedding_attempts=4,core_count=20):
    start=time.perf_counter();g=construct(str(seed),region,core_count);errors,proof=base.validate_graph(g)
    notes=diagnostics(g);direction_errors=validate_region_intent(g);catalog=base.default_catalog()
    errors+=direction_errors
    layout=base.embed(g,'R2/'+str(seed),catalog,region,attempts=embedding_attempts) if not errors else {'ok':False,'reason':'invalid_logic'}
    failures=errors[:]
    if not layout['ok']:failures.append(layout.get('reason','embedding_failed'))
    if layout['ok']:
        geometric=base.validate_layout(g,layout)
        if geometric:layout['ok']=False;failures+=geometric
    mission={'entry':g['entry'],'goal':g['goal'],'objectives':[{'id':n['id'],'role':n['role'],'label':n['label'],'reward':n['reward']} for n in g['nodes'] if n['role'] not in ['challenge','hub']],
             'dependency_edges':[{'from':g['mission_policy']['boss_forecourt'],'to':'boss','type':'boss_access'}], 'rewrite_log':g['rewrite_log']}
    initial,states,trans,_=base.state_space(g)
    state_cost=base.shortest_states(initial,trans)
    actual_goal_cost=min(v for state,v in state_cost.items() if state[0]==g['goal'])
    m={'schema':'mapgen-experiment/v1','id':f'{region}-R2-{seed}','version':VERSION,'algorithm':'R2 regional network','region':region,'seed':str(seed),
       'content_kind':'synthetic_spatial_proxy','catalog_digest':base.digest(catalog),'catalog_provenance':catalog['provenance'],
       'mission_graph':mission,'exploration_graph':g,'logic_validation':{'ok':not errors,**proof},'layout':layout,
       'metrics':{'node_count':len(g['nodes']),'edge_count':len(g['edges']),
                  'main_completion_cost':round(actual_goal_cost,3),
                  'cost_scope':'R2 abstract traversal estimates; not comparable to v1 constant unit edges or real seconds',
                  'topology_wl_signature':base.topology_signature(g),'experience_wl_signature':base.topology_signature(g,True)},
       'regional_diagnostics':notes,'regional_intent_validation':{'ok':not direction_errors,'errors':direction_errors},'failures':failures,'physics':{'status':'unverified','reason':'same synthetic masks as v1; no actual module transfers or Motor'},
       'subjective':{'status':'unverified'},'runtime_admitted':False,
       'performance':{'generation_ms':round((time.perf_counter()-start)*1000,3)}}
    m['deterministic_digest']=base.digest({k:v for k,v in m.items() if k!='performance'})
    return m


def benchmark(seeds,output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True);runs=[]
    for region in REGIONS:
        for seed in range(seeds):
            try:r=generate(str(seed),region)
            except ValueError as error:
                r={'schema':'mapgen-experiment/v1','id':f'{region}-R2-{seed}','version':VERSION,'algorithm':'R2 regional network','region':region,'seed':str(seed),
                   'logic_validation':{'ok':False},'layout':{'ok':False,'reason':'regional_construction_failed'},'failures':[str(error)],'physics':{'status':'unverified'},'subjective':{'status':'unverified'},'runtime_admitted':False}
            runs.append(r);print(region,seed,'logic',r['logic_validation']['ok'],'layout',r['layout']['ok'],r['failures'],flush=True)
    summary={'schema':'map-notes/regional-network-batch/v2','seed_range':[0,seeds-1],'total':len(runs),'logic_passes':sum(r['logic_validation']['ok'] for r in runs),'layout_passes':sum(r['layout']['ok'] for r in runs),
        'regional_direction_passes':sum(r.get('regional_intent_validation',{}).get('ok',False) for r in runs),
        'physics':'unverified','main_costs':sorted({r['metrics']['main_completion_cost'] for r in runs if 'metrics'in r}),
        'limitations':['Different topology budget from v1; no quality ranking','Planar proximity construction is a direction prototype, not final mission-space grammar','Synthetic spaces; no actual movement or human exploration evidence'],
        'source_sha256':__import__('hashlib').sha256(Path(__file__).read_bytes()).hexdigest(),
        'reused_v1_component_sha256':__import__('hashlib').sha256(Path(base.__file__).read_bytes()).hexdigest(),
        'topology_fingerprints':len({r['metrics']['topology_wl_signature'] for r in runs if 'metrics'in r})}
    (output/'runs.json').write_text(json.dumps({'schema':'mapgen-runs/v1','summary':summary,'runs':runs},ensure_ascii=False,separators=(',',':')))
    (output/'summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
    return summary

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--seeds',type=int,default=20);p.add_argument('--output',required=True)
    a=p.parse_args();print(json.dumps(benchmark(a.seeds,a.output),ensure_ascii=False,indent=2))
