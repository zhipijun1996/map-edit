"""Consume explicit ordered Port programs, never infer a common-centre route."""
import copy

def route_section(compiled,steps,ordinal):
    step=steps[ordinal];eid,fr,to=step['edge_id'],step['from'],step['to'];nodes=compiled['nodes'];edge=compiled['edges'][eid]
    path=edge['forward_waypoints']if edge['from']==fr else edge['reverse_waypoints']
    if not path:raise ValueError('missing_declared_physical_direction/'+eid+'/'+fr)
    source=nodes[fr];incoming=steps[ordinal-1]['edge_id']if ordinal else source.get('center_port')
    matrix=source.get('port_transitions',{})
    if matrix:
        key=str(incoming)+'>'+eid
        if key in matrix:before=matrix[key]
        elif incoming==eid:before=[dict(kind='walk',target=copy.deepcopy(source['ports'][eid]['target']))]
        else:raise ValueError('unsupported_ordered_port_pair/'+fr+'/'+key)
    else:before=source['center_to_port'][eid]
    after=[]if nodes[to].get('port_transitions')else nodes[to]['port_to_center'][eid]
    return [dict(copy.deepcopy(v),assembly_phase='module_traversal',assembly_node=fr)for v in before]+[dict(copy.deepcopy(v),assembly_phase='seam_transfer',assembly_node=None)for v in path]+[dict(copy.deepcopy(v),assembly_phase='module_traversal',assembly_node=to)for v in after]

def ingress_target(compiled,node,steps):
    n=compiled['nodes'][node]
    if not n.get('port_transitions'):return n['center']
    if node==compiled['exploration_graph']['entry']:return n['center']
    incoming=next((s['edge_id']for s in steps if s['to']==node),None)
    return n['ports'][incoming]['target']if incoming else n['center']
