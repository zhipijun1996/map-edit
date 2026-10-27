"""Compile the user's regional targets into explicit, separately gated budgets."""
import copy,json,math
from pathlib import Path
from ..director import regional

REWARD_KINDS=['major_item','currency','recovery','shop','hidden_collectible']
RETURN_KINDS={'foldback','loop_back','merge'}
DEFAULT=Path(__file__).with_name('plains-policy.json')

def load(path=DEFAULT):
    p=json.loads(Path(path).read_text())
    if p.get('schema')!='map-notes/graph-block-module-policy/v1':raise ValueError('unsupported_block_policy')
    if type(p['block_size'])is not int or p['block_size']<32 or p['block_size']%2:raise ValueError('invalid_block_size')
    for key in ['module_instances','main_routes','main_route_modules','reward_branches','reward_branch_modules','junctions','landmarks']:
        lo,hi=p['targets'][key]
        if type(lo)is not int or type(hi)is not int or not 0<=lo<=hi:raise ValueError('invalid_count_range/'+key)
    if set(p['reward_budgets'])!=set(REWARD_KINDS):raise ValueError('reward_categories_must_be_separate')
    if not 0<p['routes']['maximum_pairwise_edge_jaccard']<1:raise ValueError('invalid_route_difference_budget')
    kinds=p['routes']['return_kinds']
    if not kinds or len(kinds)!=len(set(kinds))or not set(kinds)<=RETURN_KINDS:raise ValueError('invalid_required_return_kinds')
    return p

def principal_routes(graph,maximum=3):
    """Reuse R2 route search. This selects responsibilities, not new topology."""
    # Native graphs declare their actual routes; do not silently replace them
    # with the older R2 classifier (which only sees regional_route edges).
    if 'principal_routes'in graph:return copy.deepcopy(graph['principal_routes'])
    g=copy.deepcopy(graph);prep=g.get('mission_policy',{}).get('boss_forecourt',g['goal']);g['mission_policy']=dict(g.get('mission_policy',{}),boss_forecourt=prep)
    for e in g['edges']:e.setdefault('purpose','regional_route')
    paths=regional.approach_routes(g)
    if maximum<=2:return paths[:maximum]
    existing={tuple(r['nodes'])for r in paths}
    blocked_candidates=[]
    for route in paths:
        for a,b in zip(route['nodes'],route['nodes'][1:]):
            for e in g['edges']:
                if {e['from'],e['to']}=={a,b}:
                    cost,nodes=regional.shortest_path(g,g['entry'],prep,frozenset([e['id']]),core_only=True)
                    if nodes and tuple(nodes)not in existing:blocked_candidates.append(dict(nodes=nodes,cost=cost))
    def similarity(a,b):
        x={frozenset(v)for v in zip(a,a[1:])};y={frozenset(v)for v in zip(b,b[1:])};return len(x&y)/max(1,len(x|y))
    if blocked_candidates:
        third=min(blocked_candidates,key=lambda r:(max(similarity(r['nodes'],p['nodes'])for p in paths),r['cost'],r['nodes']));paths.append(third)
    return paths[:maximum]

def branch_review(g,branch):
    """Return modes extend, rather than misuse, the older distinct-rejoin rule."""
    errors=[];kind=branch.get('kind');chain=[branch['entry']]+branch['nodes'];reward=branch['reward']
    ids={n['id']for n in g['nodes']}
    if any(k not in ids for k in chain):return ['branch_node_missing']
    if not branch['nodes']or len(chain)!=len(set(chain)):errors.append('branch_chain_not_simple')
    if reward not in branch['nodes']:errors.append('reward_not_on_branch')
    arcs=regional.base.expand_arcs(g);edge=lambda a,b:any(other==b for other,_ in arcs[a])
    if any(not edge(a,b)for a,b in zip(chain,chain[1:])):errors.append('branch_approach_disconnected')
    if kind=='foldback':
        if branch.get('rejoin',branch['entry'])!=branch['entry']:errors.append('foldback_must_return_to_entry')
        if any(not edge(b,a)for a,b in zip(chain,chain[1:])):errors.append('foldback_reverse_missing')
    elif kind=='loop_back':
        if branch.get('rejoin',branch['entry'])!=branch['entry']:errors.append('loop_back_must_return_to_entry')
        returns=[e for e in g['edges']if e['from']==reward and e['to']==branch['entry']and not e['bidirectional']]
        if not returns:errors.append('directed_loop_return_missing')
        if edge(branch['entry'],reward):errors.append('loop_return_has_reverse_bypass')
    elif kind=='merge':
        if branch.get('rejoin')not in ids or branch['rejoin']in branch['nodes']or branch['rejoin']==branch['entry']:errors.append('invalid_merge_target')
        elif not edge(reward,branch['rejoin']):errors.append('merge_return_missing')
    else:errors.append('unknown_branch_return_kind')
    return errors

def review(graph,policy,physical=None,timing=None):
    errors=[];unknown=[];logical,proof=regional.base.validate_graph(graph);errors+=logical
    routes=principal_routes(graph,policy['targets']['main_routes'][1]);target=policy['targets'];nodes=graph['nodes']
    def count(key,value):
        lo,hi=target[key]
        if not lo<=value<=hi:errors.append(key+'_outside_target')
    count('module_instances',len(nodes));count('main_routes',len(routes))
    arcs=regional.base.expand_arcs(graph);route_ids=set();route_paths=set()
    optional={n for b in graph.get('branches',[])for n in b['nodes']}
    destinations={graph['goal'],graph.get('mission_policy',{}).get('boss_forecourt',graph['goal'])}
    for i,route in enumerate(routes):
        path=route['nodes'];label=route.get('id',str(i))
        if label in route_ids or tuple(path)in route_paths:errors.append('duplicate_principal_route')
        route_ids.add(label);route_paths.add(tuple(path))
        if not path or path[0]!=graph['entry']or path[-1]not in destinations:errors.append('principal_route_endpoint_mismatch')
        if len(path)!=len(set(path)):errors.append('principal_route_not_simple')
        if any(k not in arcs for k in path):errors.append('principal_route_node_missing')
        elif any(not any(peer==b for peer,_ in arcs[a])for a,b in zip(path,path[1:])):errors.append('principal_route_directed_edge_missing')
        if set(path)&optional:errors.append('principal_route_enters_optional_branch')
        if not target['main_route_modules'][0]<=len(route['nodes'])<=target['main_route_modules'][1]:errors.append('main_route_length_outside_target')
    for i,a in enumerate(routes):
        x={frozenset(v)for v in zip(a['nodes'],a['nodes'][1:])}
        for b in routes[i+1:]:
            y={frozenset(v)for v in zip(b['nodes'],b['nodes'][1:])}
            if len(x&y)/max(1,len(x|y))>policy['routes']['maximum_pairwise_edge_jaccard']:errors.append('routes_too_similar')
    branches=graph.get('branches',[]);count('reward_branches',len(branches))
    actual_kinds={b.get('kind')for b in branches}
    for kind in policy['routes']['return_kinds']:
        if kind not in actual_kinds:errors.append('required_return_kind_missing/'+kind)
    core=set(graph.get('core_nodes',[]))|{k for r in routes for k in r['nodes']}
    for b in branches:
        errors += [b['id']+'/'+e for e in branch_review(graph,b)]
        if b['entry']not in core:errors.append(b['id']+'/branch_entry_not_on_main_network')
        if b.get('kind')=='merge'and b.get('rejoin')not in core:errors.append(b['id']+'/merge_not_on_main_network')
        if not target['reward_branch_modules'][0]<=len(b['nodes'])<=target['reward_branch_modules'][1]:errors.append('reward_branch_length_outside_target')
    degree={n['id']:sum(n['id']in [e['from'],e['to']]for e in graph['edges'])for n in nodes}
    count('junctions',sum(v>=3 for v in degree.values()));count('landmarks',len(graph.get('landmarks',[])))
    sites=graph.get('reward_allocations',[]);unknown.append('meaningful_content_interval_requires_verified_module_semantics');counts={k:sum(s['kind']==k for s in sites)for k in REWARD_KINDS}
    for kind,n in counts.items():
        lo,hi=policy['reward_budgets'][kind]['count']
        if not lo<=n<=hi:errors.append('reward_count/'+kind)
        budget=policy['reward_budgets'][kind]['value_budget']
        if budget is None:unknown.append('uncalibrated_value_budget/'+kind)
        elif any(type(s.get('value'))not in [int,float]for s in sites if s['kind']==kind):unknown.append('unpriced_reward/'+kind)
        elif sum(s['value']for s in sites if s['kind']==kind)>budget:errors.append('reward_value_budget/'+kind)
    major=[s for s in sites if s['kind']=='major_item'];high=sum(s.get('high_value',False)for s in major)
    if not policy['high_value_rewards'][0]<=high<=policy['high_value_rewards'][1]:errors.append('high_value_reward_count')
    if not physical:unknown.append('whole_map_physics_not_verified')
    elif not physical.get('all_passed'):errors.append('whole_map_physics_failed')
    if not timing or timing.get('source')!='human_playtest':unknown.append('human_playtime_not_calibrated')
    else:
        for key in ['shortest_human_seconds','exploration_human_seconds']:
            if not target[key][0]<=timing[key]<=target[key][1]:errors.append(key+'_outside_target')
    if not any(n.get('role')=='boss'and n.get('encounter_verified')for n in nodes):unknown.append('actual_boss_encounter_missing')
    return dict(ok=not errors,declared_requirements_satisfied=not errors and not unknown,production_ready=False,admission='Canonical trusted physics / Boss / human review gates remain authoritative',errors=sorted(set(errors)),unknown=sorted(set(unknown)),routes=routes,reward_counts=counts,logic=proof,
        actual_return_kinds=sorted(k for k in actual_kinds if k is not None),required_return_kinds=policy['routes']['return_kinds'][:],
        scope='Policy acceptance; abstract success never substitutes for complete gameplay, economy or human timing')


def materialization_review(graph,compiled):
    """Current one-node/one-placement adapter must preserve its actual input.

    Composite Macro internals remain inside their owning placement. A future
    many-placement realization needs an explicit mapping, not an edited graph.
    """
    from pcg.prototype.factory.core.quality import digest
    errors=[]
    if digest(graph)!=digest(compiled['exploration_graph']):errors.append('exploration_graph_changed_during_materialization')
    expected_nodes=[n['id']for n in graph['nodes']];actual_nodes=[m['id']for m in compiled['modules']]
    expected_edges=[e['id']for e in graph['edges']];actual_edges=[s['id']for s in compiled['seams']]
    if sorted(expected_nodes)!=sorted(actual_nodes):errors.append('blueprint_placement_nodes_mismatch')
    if sorted(expected_edges)!=sorted(actual_edges):errors.append('blueprint_seams_mismatch')
    by={m['id']:m for m in compiled['modules']}
    for edge in graph['edges']:
        for node in [edge['from'],edge['to']]:
            if node in by and edge['id']not in by[node]['ports']:errors.append('blueprint_edge_port_missing/'+edge['id']+'/'+node)
    return dict(ok=not errors,errors=errors,input_graph_sha256=digest(graph),materialized_graph_sha256=digest(compiled['exploration_graph']),
                scope='Identity and edge/Port correspondence only; no logical, physical or human design pass')

def demands(graph,policy):
    """Map -> Module requests, preserving every requested edge and objective."""
    from pcg.prototype.factory.core.quality import digest
    rows=[];routes=principal_routes(graph,policy['targets']['main_routes'][1])
    for n in graph['nodes']:
        es=[e for e in graph['edges']if n['id']in [e['from'],e['to']]]
        roles=n.get('functional_roles',[{'hub':'junction','start':'entry','prep':'boss_forecourt','boss':'boss','reward':'reward','rest':'open_space'}.get(n['role'],'traversal')])
        rows.append(dict(schema='map-notes/challenge-specification/v1',id='block-demand/'+n['id'],map_seed=graph.get('seed'),region=graph.get('region','plains'),
            exploration_sha256=digest(graph),policy_sha256=digest(policy),
            objective=dict(node=n['id'],roles=roles,main_or_optional=n.get('intent','UNKNOWN'),preserve_all_edges=[e['id']for e in es]),
            block_grid=dict(size=policy['block_size'],shape='connected_polyomino',port_anchors='boundary_cell_centers',map_added_terrain=0),
            ports=dict(count=len(es),directions='joint_space_search',required_pairs='explicit_ordered_matrix'),
            capabilities=dict(version=1,status='defined',allOf=graph['initial_abilities'],anyOfGroups=[]),
            resource_state=dict(entry='UNKNOWN until measured state contract',exit='UNKNOWN until measured state contract',reset_between_components=False),
            relations='UNKNOWN until exact module directions are independently verified',
            difficulty=dict(intent=n.get('risk','UNKNOWN'),human_score=None),
            route_membership=dict(main=[r.get('id',str(i))for i,r in enumerate(routes)if n['id']in r['nodes']],branches=[b['id']for b in graph['branches']if n['id']in [b['entry'],b.get('rejoin')]+b['nodes']]),
            rewards=[s for s in graph.get('reward_allocations',[])if s['node']==n['id']],
            return_conditions=dict(branches=[b for b in graph.get('branches',[])if n['id']in b['nodes']]),
            budget=dict(generator_calls=4,local_revisions=2,may_delete_required_edges=False)))
    return rows
