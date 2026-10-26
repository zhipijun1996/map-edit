"""Map intent gate over the existing R2 graph and actual assembled objects.

This does not generate graphs, simulate physics, edit Module objects, or turn
declared bidirectionality into physical proof.
"""
import copy,json,math
from pathlib import Path
from ..director import REPO,regional

TARGETS=Path(__file__).with_name('design-targets-v1.json')
def targets():return json.loads(TARGETS.read_text())

def graph_review(graph,policy=None):
    p=policy or targets();g=copy.deepcopy(graph)
    for e in g['edges']:e.setdefault('purpose','unspecified')
    errors,logic=regional.base.validate_graph(g)
    errors=['logic/'+e for e in errors]
    ids={n['id']for n in g['nodes']}
    declared=g.get('core_nodes')
    if not declared:
        if p['topology']['require_regional_core_contract']:errors.append('regional_core_contract_missing')
        core=ids-{g['entry'],g['goal']}
    else:core=set(declared)
    if not core or not core<=ids:return dict(ok=False,errors=errors+['invalid_regional_core'],logic=logic)
    # Reuse R2's core intent checks when the original contract is available.
    if declared:
        needed=['branches','mission_policy']
        if all(k in g for k in needed):errors+=regional.validate_region_intent(g)
        else:errors.append('regional_mission_contract_incomplete')
    pairs=[(e['from'],e['to'])for e in g['edges']if e['from']in core and e['to']in core]
    cuts=regional.articulation_nodes(core,pairs)
    if len(cuts)>p['topology']['maximum_core_articulations']:errors.append('mandatory_core_chain')
    reentrant=[n for n in sorted(core)if math.isfinite(regional.shortest_path(g,g['entry'],n)[0])and math.isfinite(regional.shortest_path(g,n,g['entry'])[0])]
    fraction=len(reentrant)/len(core)
    if fraction<p['topology']['minimum_reentrant_core_fraction']:errors.append('insufficient_declared_core_reentry')
    unavoidable=[]
    for n in sorted(ids-{g['entry'],g['goal']}):
        blocked=frozenset(e['id']for e in g['edges']if n in [e['from'],e['to']])
        _,states,_,_=regional.base.state_space(g,disabled_edges=blocked)
        if not any(s[0]==g['goal']for s in states):unavoidable.append(n)
    return dict(ok=not errors,errors=sorted(set(errors)),logic=logic,core_articulations=cuts,reentrant_core_nodes=reentrant,reentrant_core_fraction=fraction,
        goal_unavoidable_nodes=unavoidable,scope='Core reentry uses initial basic abilities; goal bypass uses existing monotonic state validator. Neither is physical proof')

def reward_requests(graph,policy=None):
    """Allocate only declared optional objectives; ordinary challenges get zero.

    Returns ordinary ChallengeSpecification.risk_reward fields, never removes
    a chest from an immutable source Module or silently changes its objective.
    """
    p=(policy or targets())['rewards'];g=copy.deepcopy(graph);nodes={n['id']:n for n in g['nodes']}
    for e in g['edges']:e.setdefault('purpose','unspecified')
    # Boss access may be earned; exclusion proof compares the full declared
    # monotonic mission state space, not only an initial-state shortest path.
    rows={};errors=[];assigned=[]
    for key,n in nodes.items():
        value=n.get('reward',0);shop=n['role']=='shop'
        directive=dict(reward_authority='map_director',max_reward_sites=0,max_shop_sites=1 if shop else 0,value=0,
            optional=False,preserve_required_mechanic=True,source_change='New canonical version and fresh whole-map verification required; no in-place filtering')
        if value:
            optional=n['role']=='reward'
            blocked=frozenset(e['id']for e in g['edges']if key in [e['from'],e['to']])
            _,states,_,_=regional.base.state_space(g,disabled_edges=blocked)
            optional=optional and any(s[0]==g['goal']for s in states)
            if not optional:errors.append('reward_not_optional_objective/'+key)
            # The original R2 expedition contract supplies the required
            # distinct rejoin and earned return, not a renamed recovery port.
            branch=next((b for b in g.get('branches',[])+g.get('reward_routes',[])if b['reward']==key),None)
            if not branch or branch['entry']==branch['rejoin']:errors.append('reward_excursion_contract_missing/'+key)
            cost=regional.shortest_path(g,branch['entry'],key,initial_only=False)[0]if branch else 0
            if cost<p['minimum_optional_detour_cost']:errors.append('reward_detour_too_shallow/'+key)
            if branch and branch.get('return_mode')=='existing_core_loop':
                _,reachable,transitions,_=regional.base.state_space(g)
                reward_states=[s for s in reachable if s[0]==key]
                # Reuse the state transition graph for distinct-rejoin return.
                pending=list(reward_states);seen=set(pending)
                while pending:
                    for nxt,_ in transitions[pending.pop()]:
                        if nxt not in seen:seen.add(nxt);pending.append(nxt)
                if not any(s[0]==branch['rejoin']for s in seen):errors.append('reward_core_loop_return_missing/'+key)
                return_condition='Existing distinct-rejoin regional loop; no newly earned shortcut claimed'
            else:return_condition='Earned shortcut plus distinct rejoin; actual state transfer UNKNOWN until whole-map test'
            directive.update(max_reward_sites=1,value=value,optional=optional,require_return=True,
                expedition=branch['id']if branch else None,return_conditions=return_condition)
            assigned.append(key)
        rows[key]=directive
    if len(assigned)>p['maximum_chests']:errors.append('chest_budget_exceeded')
    if len(assigned)/max(1,len(nodes))>p['maximum_chest_node_fraction']:errors.append('chest_density_exceeded')
    if sum(n.get('reward',0)for n in nodes.values())>p['maximum_currency']:errors.append('currency_budget_exceeded')
    if sum(n['role']=='shop'for n in nodes.values())>p['maximum_shops']:errors.append('shop_budget_exceeded')
    return dict(ok=not errors,errors=errors,requests=rows,chest_nodes=assigned,scope='Design demands only; no chest, merchant or currency instantiated')

def review(compiled,policy=None):
    p=policy or targets();g=compiled['exploration_graph'];graph=graph_review(g,p);allocation=reward_requests(g,p)
    errors=graph['errors']+allocation['errors'];sites=compiled['case'].get('reward_sites',[]);shops=compiled['case'].get('shop_sites',[])
    actual={};seen=[]
    for m in compiled['modules']:
        local=m['case'].get('reward_sites',[]);actual[m['id']]=len(local)
        seen.extend(m['id']+'/'+s['id']for s in local)
        request=allocation['requests'][m['id']]
        if len(local)>request['max_reward_sites']:errors.append('module_reward_not_allocated/'+m['id'])
        if len(local)>p['rewards']['maximum_chests_per_module']:errors.append('module_reward_density_exceeded/'+m['id'])
        if len(local)!=request['max_reward_sites']:errors.append('reward_request_not_materialized/'+m['id'])
        if sum(s['amount']for s in local)!=request['value']:errors.append('reward_value_not_materialized/'+m['id'])
        if len(m['case'].get('shop_sites',[]))!=request['max_shop_sites']:errors.append('shop_request_not_materialized/'+m['id'])
    if sorted(seen)!=sorted(s['id']for s in sites):errors.append('reward_object_provenance_mismatch')
    currency=sum(s['amount']for s in sites)
    if len(sites)>p['rewards']['maximum_chests']:errors.append('physical_chest_budget_exceeded')
    if len(sites)/max(1,len(g['nodes']))>p['rewards']['maximum_chest_node_fraction']:errors.append('physical_chest_density_exceeded')
    if currency>p['rewards']['maximum_currency']:errors.append('physical_currency_budget_exceeded')
    if len(shops)>p['rewards']['maximum_shops']:errors.append('physical_shop_budget_exceeded')
    return dict(schema='pcg/map-design-review/v1',ok=not errors,errors=sorted(set(errors)),graph=graph,allocation=allocation,
        actual_chests=len(sites),actual_currency=currency,actual_shops=len(shops),chests_by_module=actual,
        scope='Intent and actual object budget; neither aesthetic approval nor physics pass',production_admitted=False)
