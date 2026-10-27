"""Routes come from the actual principal paths and all three branch contracts."""
import copy
from ..block_grid.policy import principal_routes
from ..r2_full.orchestrate import path_to,state_after,edge_cover_route
from ..region_scale.materialize import case_for
from ..director import REPO
from ..shape_search.search import translated


def steps(g,nodes):
    out=[]
    for a,b in zip(nodes,nodes[1:]):
        e=next(e for e in g['edges']if(e['from']==a and e['to']==b)or(e['bidirectional']and e['to']==a and e['from']==b))
        out.append(dict(edge_id=e['id'],**{'from':a,'to':b}))
    return out


def base(c,path,name,required=()):
    v=case_for(c,path,name);v.update(title='风铃平原 · Graph / Block / Module 联合空间候选',preview_title='同图驱动 · 多路线 · 三类奖励回程 · 原角色/机关',extra_script=str(REPO/'pcg/map_directed/graph_map/extra.gd'),required_reward_ids=list(required),map_seed=c['exploration_graph']['seed'],reward_flag_requirements=c.get('reward_flag_requirements',{}),automatic_shop_input=False)
    v['presentation_keep_clear']=[translated(r,m['spec']['placement'])for m in c['modules']for r in m['action_clearance']]
    v['presentation_areas']=[dict(id=k,identity=identity,position=c['nodes'][k]['center']['position'])for k,identity in zip(c['exploration_graph'].get('landmarks',[]),['windmill_plateau','clock_court','creek_well','repair_gallery'])]
    for n in v['r2_semantics']['nodes']:
        n['visit_targets']=[p['target']for p in c['nodes'][n['id']]['ports'].values()]
    goal=c['exploration_graph']['goal'];eid=path[-1]['edge_id'];last=c['nodes'][goal]
    visit=last.get('port_transitions',{}).get(eid+'>'+eid,[])
    for i,raw in enumerate(visit):
        leg=copy.deepcopy(raw);leg.update(id='goal-visit-'+str(i),edge_id='goal-visit',edge_from=goal,edge_to=goal,edge_terminal=False);v['pilot_program'].append(leg)
    v['required_bosses']=[b['id']for b in c['case'].get('boss_encounters',[])]
    v['map_budget_ticks']=36000
    for leg in v['pilot_program']:
        if leg['kind']=='module'and not leg.get('boss_duel'):leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
    return v


def create(c,coverage_parts=4):
    g=c['exploration_graph'];out=[];baseline=[s['id']for s in c['case']['reward_sites']if s.get('allocation',{}).get('node')==g['mission_policy']['boss_forecourt']and s.get('reward_kind')=='major_item']
    for i,route in enumerate(principal_routes(g,3)):
        nodes=route['nodes'][:]
        if nodes[-1]!=g['goal']:nodes.append(g['goal'])
        out.append(base(c,steps(g,nodes),'main-'+str(i),baseline))
    for b in g['branches']:
        state=state_after(g,(g['entry'],frozenset(g['initial_abilities']),frozenset()),g['entry']);first=steps(g,[b['entry'],b['nodes'][0]])[0];edge=next(e for e in g['edges']if e['id']==first['edge_id'])
        lead,state,_=path_to(g,state,b['entry'],edge)
        chain=[b['entry']]+b['nodes']
        if b['kind']=='foldback':chain+=list(reversed(chain[:-1]))
        else:chain+=b.get('return_nodes',[])+[b['rejoin']]
        middle=steps(g,chain)
        for s in middle:state=state_after(g,state,s['to'])
        tail,state,_=path_to(g,state,g['goal']);path=lead+middle+tail
        earned=[s['id']for s in c['case']['reward_sites']if s.get('allocation',{}).get('node')==b['reward']and s.get('reward_kind')in ['major_item','hidden_collectible']]
        v=base(c,path,'branch-'+b['id']+'-'+b['kind'],earned+baseline);v['branch_contract']=copy.deepcopy(b);out.append(v)
    if coverage_parts:
        arcs=sorted({(e['id'],e['from'],e['to'])for e in g['edges']}|{(e['id'],e['to'],e['from'])for e in g['edges']if e['bidirectional']});count=(len(arcs)+coverage_parts-1)//coverage_parts
        for i in range(0,len(arcs),count):
            requested=set(arcs[i:i+count]);v=base(c,edge_cover_route(c,requested),'arc-cover-'+str(i//count));v['r2_semantics']['requested_directed_edges']=[list(a)for a in sorted(requested)];out.append(v)
    return out
