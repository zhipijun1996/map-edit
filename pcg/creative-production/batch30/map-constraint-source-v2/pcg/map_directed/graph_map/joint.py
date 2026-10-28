"""Expose a high-degree Macro's internal shape choices to the existing solver.

The regional graph is immutable. Only local junction composition is expanded
for spatial search, then folded into the owning Macro with explicit lineage.
"""
import copy,random,math
import networkx as nx
from .domains import candidate_domains
from pcg.prototype.plains.compound_terraces import payload
from pcg.prototype.factory.core.quality import digest


def expand(graph,seed):
    planar,embedding=nx.check_planarity(nx.Graph([(e['from'],e['to'])for e in graph['edges']]))
    if not planar:raise ValueError('regional_graph_requires_nonplanar_overpass_contract')
    expanded=copy.deepcopy(graph);expanded['nodes']=[];expanded['edges']=[];owners={};bindings={};locals={};rng=random.Random(seed)
    for node in graph['nodes']:
        key=node['id'];incident=[e for e in graph['edges']if key in[e['from'],e['to']]]
        if len(incident)<=3:
            expanded['nodes'].append(copy.deepcopy(node));owners[key]=[key]
            for e in incident:bindings[(key,e['id'])]=key
            continue
        # A connected tree of three-Port junctions has exactly d external
        # mouths. Its shapes, heights and actual movements remain variables.
        count=len(incident)-2;ids=[key+'/component-'+str(i)for i in range(count)];owners[key]=ids
        local=dict(entry=ids[0],goal=ids[-1],initial_abilities=['move']+graph['initial_abilities'],nodes=[],edges=[],source='Demanded local Macro composition inside '+key)
        for i,id in enumerate(ids):
            n=dict(id=id,role='junction',grants=[],opens=[],reward=0,risk=node.get('risk',1),macro_owner=key,ideal=node.get('ideal',[0,0]),intent='Local branching/merge; not another regional graph')
            expanded['nodes'].append(n);local['nodes'].append(copy.deepcopy(n))
            if i:
                e=dict(id='macro-internal/'+key+'/'+str(i),**{'from':ids[i-1],'to':id},bidirectional=True,requires=[],switch=None,cost=0,purpose='macro_internal')
                expanded['edges'].append(e);local['edges'].append(copy.deepcopy(e))
        mouths=[ids[0],ids[0]]+ids[1:-1]+[ids[-1],ids[-1]]
        neighbors=list(embedding.neighbors_cw_order(key));offset=rng.randrange(len(neighbors));neighbors=neighbors[offset:]+neighbors[:offset]
        es=[next(e for e in incident if peer in[e['from'],e['to']])for peer in neighbors]
        for e,id in zip(es,mouths):bindings[(key,e['id'])]=id
        locals[key]=local
    for edge in graph['edges']:
        e=copy.deepcopy(edge);e['from']=bindings[(edge['from'],edge['id'])];e['to']=bindings[(edge['to'],edge['id'])];expanded['edges'].append(e)
    if not nx.check_planarity(nx.Graph([(e['from'],e['to'])for e in expanded['edges']]))[0]:raise ValueError('local_composition_changed_planarity')
    expanded.update(entry=owners[graph['entry']][0],goal=owners[graph['goal']][0],source_graph_sha256=digest(graph),spatial_constraint_expansion=True)
    return expanded,dict(owners=owners,locals=locals,external_bindings=[dict(node=k,edge=e,component=v)for(k,e),v in bindings.items()],source_graph_sha256=digest(graph),port_rotation='Planar combinatorial embedding; consecutive external leaves; no random edge permutation')


def domains(expanded,pool):
    D,A=candidate_domains(expanded,pool)
    for n in expanded['nodes']:
        if n.get('macro_owner'):
            D[n['id']]=[m for m in D[n['id']]if all(a+'>'+b in m.get('port_transitions',{})for a in m['ports']for b in m['ports']if a!=b)]
    return D,A


def fold(graph,mapping,selected):
    by={m['id']:m for m in selected};out=[]
    for node in graph['nodes']:
        key=node['id'];ids=mapping['owners'][key]
        if len(ids)==1:m=copy.deepcopy(by[ids[0]])
        else:
            origin=by[ids[0]]['spec']['placement'];local=[]
            for id in ids:
                component=copy.deepcopy(by[id]);component['spec']['placement']=[component['spec']['placement'][i]-origin[i]for i in range(2)];local.append(component)
            m=payload(mapping['locals'][key],local);m['spec']['placement']=origin;m['spec']['block_placement']=[round(v/128)for v in origin]
            m['adaptation']['joint_shape_search']=dict(original_node=key,source_graph_sha256=mapping['source_graph_sha256'],local_components=ids,geometry_and_actions_chosen_in_entire_map=True,independent_macro_physics='PENDING')
            m['selection_family']='joint_compound_junction';m['variant_id']=key+'/joint/'+m['source_version'].split(':')[-1][:16]
        m['id']=key;m['spec'].update(id='graph-demand/'+key,node_id=key,node=copy.deepcopy(node));out.append(m)
    return out
