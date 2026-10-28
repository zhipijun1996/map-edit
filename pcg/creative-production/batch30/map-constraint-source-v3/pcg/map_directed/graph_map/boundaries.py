"""Fit only source-owned shutter variants to an already rigid Module layout."""
import copy
from ..shape_search.search import intersects,translated
from ..block_grid.contracts import regions
from .domains import required_pairs
from pcg.prototype.workshop.production_loop import compile_request


def bind(graph,modules):
    by={m['id']:copy.deepcopy(m)for m in modules};log=[]
    for edge in graph['edges']:
        if edge['bidirectional']and not edge.get('switch'):continue
        condition=graph.get('condition_definitions',{}).get(edge.get('switch'),{})
        if condition.get('kind')=='knowledge'and edge['bidirectional']:
            log.append(dict(edge=edge['id'],switch=edge['switch'],physical_gate_required=False,reason='Discovery/visibility condition, no invented mechanical lock'));continue
        chosen=None;attempts=[]
        for owner in sorted([edge['from'],edge['to']],key=lambda k:(len(by[k]['ports']),k)):
            for inset in [0]:
                response=compile_request(dict(recipe='map-state-boundary/v1',module=by[owner],edge=edge,inset=inset,height=512));attempt=dict(owner=owner,inset=inset,status=response['status'],gaps=response.get('gaps',[]));attempts.append(attempt)
                if not response['modules']:continue
                m=response['modules'][0];pairs=required_pairs(graph,owner)[1]
                if any(a+'>'+b not in m['port_transitions']for a,b in pairs):attempt['gaps'].append('required_transition_removed');continue
                rect=translated(m['boundary_gates'][-1]['bounds'],m['spec']['placement']);obstructions=[]
                for peer,other in by.items():
                    if peer==owner:continue
                    foreign=regions(other)+[g['bounds']for g in other['boundary_gates']]
                    if any(intersects(rect,translated(r,other['spec']['placement']))for r in foreign):obstructions.append(peer)
                if obstructions:attempt['gaps'].append('foreign_entity_or_action_space/'+','.join(obstructions));continue
                chosen=m;break
            if chosen is not None:break
        log.append(dict(edge=edge['id'],switch=edge.get('switch'),one_way=not edge['bidirectional'],attempts=attempts,selected_owner=chosen['id']if chosen else None))
        if chosen is None:return None,log
        by[chosen['id']]=chosen
    return [by[n['id']]for n in graph['nodes']],log
