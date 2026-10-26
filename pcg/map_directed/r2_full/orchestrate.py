"""Preserved full R2 topology: concrete route assembly and bounded real execution."""
from __future__ import annotations
import argparse
import copy
import heapq
import json
from pathlib import Path
import shutil
from .compiler import compile_map
from .paths import join_waypoints
from ..director import REPO
from ..run import write
from pcg.prototype.plains.engine import PlainsEngine
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest


class FullMapEngine(PlainsEngine):
    def __init__(self,out):
        super().__init__(out,1)
        for p in sorted((REPO/'pcg/map_directed/r2_full').rglob('*')):
            if p.is_file()and p.suffix in ['.py','.gd','.json']and'__pycache__'not in p.parts:
                rel=p.relative_to(REPO/'pcg').as_posix();self.hashes[rel]=file_sha(p)
                target=self.out/'source_snapshot'/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,target)
        self.sim.runner_script=str(REPO/'pcg/map_directed/r2_full/godot/r2_runner.gd')
        self.binding.update(runner=self.sim.runner_script,source_files=self.hashes,
            source_manifest_sha256=digest(self.hashes),scope='entire preserved R2 map / no world or resource reset within route')
        write(self.out/'source_binding.json',self.binding)


def state_after(graph,state,node):
    n=next(n for n in graph['nodes']if n['id']==node)
    return (node,state[1]|frozenset(n['grants']),state[2]|frozenset(n['opens']))


def path_to(graph,start,target,require_edge=None):
    by={n['id']:n for n in graph['nodes']};adj={k:[] for k in by}
    for e in graph['edges']:
        adj[e['from']].append((e['to'],e))
        if e['bidirectional']:adj[e['to']].append((e['from'],e))
    counter=0;queue=[(0.,counter,start,[])];best={start:0.}
    while queue:
        cost,_,state,path=heapq.heappop(queue)
        if cost!=best[state]:continue
        valid=(not require_edge or(set(require_edge['requires'])<=state[1]and(not require_edge['switch']or require_edge['switch']in state[2])))
        if state[0]==target and valid:return path,state,cost
        for other,e in sorted(adj[state[0]],key=lambda q:(q[1]['id'],q[0])):
            if not set(e['requires'])<=state[1]or(e['switch']and e['switch']not in state[2]):continue
            to=state_after(graph,state,other);value=cost+e['cost']
            if value<best.get(to,float('inf')):
                counter+=1;best[to]=value
                heapq.heappush(queue,(value,counter,to,path+[{'edge_id':e['id'],'from':state[0],'to':other}]))
    raise ValueError('no_state_valid_route_to/'+target)


def logical_route(compiled,targets):
    graph=compiled['exploration_graph'];state=state_after(graph,(graph['entry'],frozenset(graph['initial_abilities']),frozenset()),graph['entry'])
    result=[]
    for target in targets:
        part,state,_=path_to(graph,state,target);result+=part
    return result


def edge_cover_route(compiled, requested=None):
    g=compiled['exploration_graph'];current=state_after(g,(g['entry'],frozenset(g['initial_abilities']),frozenset()),g['entry'])
    if requested is None:
        requested={(e['id'],e['from'],e['to'])for e in g['edges']}
        requested|={(e['id'],e['to'],e['from'])for e in g['edges']if e['bidirectional']}
    remaining=set(requested);steps=[]
    edges={e['id']:e for e in g['edges']}
    for _ in range(160):
        if not remaining:break
        candidates=[]
        for eid,fr,to in sorted(remaining):
            path,at,cost=path_to(g,current,fr,edges[eid]);candidates.append((cost+edges[eid]['cost'],eid,fr,to,path,at))
        _,eid,fr,to,path,current=min(candidates,key=lambda x:x[:4])
        addition=path+[{'edge_id':eid,'from':fr,'to':to}];steps+=addition
        current=state_after(g,current,to)
        for step in addition:remaining.discard((step['edge_id'],step['from'],step['to']))
    if remaining:raise ValueError('directed_edge_cover_budget_exhausted')
    tail,_,_=path_to(g,current,g['goal']);return steps+tail


def partitioned_cover(compiled, count=5):
    """Each tour starts at the original entry and earns its own graph flags.

    Splitting bounds a policy; it never teleports between edges within a tour
    or claims all junction state combinations from these finite witnesses.
    """
    graph=compiled['exploration_graph']
    arcs=[(e['id'],e['from'],e['to']) for e in graph['edges']]
    arcs += [(e['id'],e['to'],e['from']) for e in graph['edges'] if e['bidirectional']]
    arcs=sorted(arcs,key=lambda a:(int(a[0][1:]),a[1],a[2]))
    size=(len(arcs)+count-1)//count
    cases=[]
    for index in range(0,len(arcs),size):
        requested=set(arcs[index:index+size])
        case=make_case(compiled,edge_cover_route(compiled,requested),'coverage-'+str(index//size+1))
        if len(case['pilot_program'])>2048: raise ValueError('bounded_coverage_program_too_large')
        case['r2_semantics']['requested_directed_edges']=[list(a)for a in sorted(requested)]
        cases.append(case)
    return cases


def make_case(compiled,steps,name,goal=None,required_rewards=None):
    graph=compiled['exploration_graph'];case=copy.deepcopy(compiled['case'])
    nodes=compiled['nodes'];program=[];visited=[graph['entry']]
    first={'kind':'walk','target':copy.deepcopy(nodes[graph['entry']]['center'])}
    program.append({**first,'id':'initial-supported-entry','edge_id':'entry','budget_ticks':180})
    for ordinal,step in enumerate(steps):
        eid,fr,to=step['edge_id'],step['from'],step['to'];edge=compiled['edges'][eid]
        path=edge['forward_waypoints']if edge['from']==fr else edge['reverse_waypoints']
        if not path:raise ValueError('missing_declared_physical_direction/'+eid+'/'+fr)
        if any(n.get('port_transitions')for n in nodes.values()):
            from ..content_domains.routes import route_section
            section=join_waypoints(route_section(compiled,steps,ordinal))
        else:section=join_waypoints(nodes[fr]['center_to_port'][eid],path,nodes[to]['port_to_center'][eid])
        for index,waypoint in enumerate(section):
            leg=copy.deepcopy(waypoint);leg.update(id=f'{ordinal:03d}-{eid}-{index:03d}',edge_id=eid,
                edge_from=fr,edge_to=to,edge_terminal=index==len(section)-1,budget_ticks=360)
            program.append(leg)
        visited.append(to)
    goal=goal or visited[-1]
    goal_target=nodes[goal]['ports'][steps[-1]['edge_id']]['target']if steps and nodes[goal].get('port_transitions')else nodes[goal]['center']
    case.update(id='r2-full-'+name,goal=copy.deepcopy(goal_target['region']),
        exit_port=copy.deepcopy(goal_target['position']),pilot_program=program,
        map_budget_ticks=min(36000,max(3600,len(program)*90)),noise={},
        extra_script=str(REPO/'pcg/map_directed/r2_full/state_extra.gd'),extra_required=True)
    from ..content_domains.routes import ingress_target
    gates=copy.deepcopy(compiled['gate_specs'])
    for gate in gates:
        gate['bounds']=[gate['x'],gate['y'],gate['w'],gate['h']]
    case['gate_specs']=gates
    case['r2_semantics']={'nodes':[dict(id=k,target=(ingress_target(compiled,k,steps)if v.get('port_transitions')else v['center']),opens=v['opens'],reward=v['reward'],label=v['label'])for k,v in nodes.items()],
        'required_nodes':list(dict.fromkeys(visited)),'required_rewards':required_rewards or[],
        'source_graph_sha256':compiled['source']['graph_sha256'],'full_nodes':len(nodes),'full_edges':len(compiled['edges']),
        'logical_route':steps,'quality_scope':compiled['status']}
    return case


def run(name,mode='calibrate',hazards=False):
    out=REPO/'pcg/results'/name
    if out.exists():raise ValueError('immutable_full_map_run_exists')
    out.mkdir(parents=True);compiled=compile_map(static_gap_hazards=hazards)
    write(out/'compiled.json',compiled)
    g=compiled['exploration_graph']
    if mode=='calibrate':
        neighbour=next(e['to']if e['from']==g['entry']else e['from']for e in g['edges']if g['entry']in[e['from'],e['to']])
        steps=logical_route(compiled,[neighbour]);cases=[make_case(compiled,steps,'first-edge',goal=neighbour)]
    elif mode=='main':cases=[make_case(compiled,logical_route(compiled,[g['goal']]),'main')]
    elif mode=='cover':cases=partitioned_cover(compiled)
    else:
        reward=[n['id']for n in g['nodes']if n['reward']]
        cases=[make_case(compiled,logical_route(compiled,[g['goal']]),'main')]
        for node in reward:
            cases.append(make_case(compiled,logical_route(compiled,[node,g['entry'],g['goal']]),'reward-'+node,required_rewards=[node]))
    write(out/'cases.json',{'cases':cases})
    print('FULL R2',len(g['nodes']),len(g['edges']),'platforms',len(compiled['case']['platforms']),
        'routes',[(c['id'],len(c['pilot_program']))for c in cases],flush=True)
    engine=FullMapEngine(out/'physics');rows=[]
    for c,result,evidence in engine.run(cases,'full-r2-policies'):
        rows.append({'case_id':c['id'],'ok':result['ok'],'reason':result['reason'],'ticks':result.get('ticks'),
            'legs':result.get('pilot',{}).get('legs_completed'), 'total_legs':len(c['pilot_program']),
            'failure':result.get('pilot',{}).get('failure'),'mechanics':result.get('extra'),'evidence':evidence})
        print(json.dumps(rows[-1],ensure_ascii=False)[:1500],flush=True)
    write(out/'summary.json',{'source':compiled['source'],'coverage':compiled['coverage'],'rows':rows,
        'quality':'not_admitted; full navigation candidate under validation, not finished challenge content'})
    return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--name',required=True);p.add_argument('--mode',choices=['calibrate','main','cover','routes'],default='calibrate');p.add_argument('--hazards',action='store_true')
    a=p.parse_args();print(run(a.name,a.mode,a.hazards))
