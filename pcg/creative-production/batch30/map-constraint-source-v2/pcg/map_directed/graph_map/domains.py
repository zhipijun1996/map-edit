"""Actual directed Port assignments; no node-name, layer or family recipes."""
import copy,itertools
from ..content_domains.build import tags

def bind(source,mapping):
    """Permutations share immutable geometry/programs until CSP selects a value.

    Copying a six-Port Macro720times otherwise duplicates its30 long programs.
    Only Port names and demand metadata vary; selected payloads are deep-copied
    by the existing search before placement/export.
    """
    m=copy.copy(source)
    for name in ['ports','port_to_center','center_to_port']:
        m[name]={mapping[k]:(dict(v,id=mapping[k])if name=='ports'else v)for k,v in source.get(name,{}).items()}
    for name in ['port_transitions','transition_options','transition_sources']:
        m[name]={mapping[a]+'>'+mapping[b]:v for key,v in source.get(name,{}).items()for a,b in[key.split('>')]}
    if source.get('center_port'):m['center_port']=mapping[source['center_port']]
    m['block_grid']=dict(source['block_grid'],port_bindings=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()])
    return m



def required_pairs(graph,node):
    incident=[e for e in graph['edges']if node in [e['from'],e['to']]]
    entering=[e['id']for e in incident if e['to']==node or e['bidirectional']]
    leaving=[e['id']for e in incident if e['from']==node or e['bidirectional']]
    pairs={(a,b)for a in entering for b in leaving if a!=b}
    if len(incident)==1 and entering and leaving:pairs.add((entering[0],leaving[0]))
    return incident,pairs


def assignments(graph,node,module):
    """Exact Port count; side directions and unequal heights remain choices."""
    incident,pairs=required_pairs(graph,node['id']);ports=module['ports']
    if node.get('role')=='boss'and not module.get('boss_contract'):return [],['actual_boss_encounter_required']
    if node.get('role')!='boss'and module.get('boss_contract'):return [],['boss_content_requires_boss_responsibility']
    if len(incident)!=len(ports):return [],['port_count']
    # R2 lists unlockable actions; original Motor contracts also name base
    # locomotion. This is an explicit schema bridge, never a new unlock.
    available={'move'}|set(graph['initial_abilities'])
    if not set(module['motion_contract']['capabilities'])<=available:return [],['capabilities']
    matrix=module.get('port_transitions',{})
    if not matrix:return [],['ordered_port_pairs_require_real_verification']
    objectives=node.get('required_features',[]);edges=[e['id']for e in incident];matches=[]
    for permutation in itertools.permutations(ports):
        binding=dict(zip(edges,permutation))
        if any(binding[a]+'>'+binding[b]not in matrix for a,b in pairs):continue
        if objectives and not any(set(objectives)<=tags(module,binding[a]+'>'+binding[b])for a,b in pairs):continue
        mapping={p:e for e,p in binding.items()};matches.append(mapping)
    return matches,[]if matches else['required_ordered_port_pairs_or_actions_missing']


def candidate_domains(graph,pool):
    domains={};audit=[]
    for node in graph['nodes']:
        values=[]
        for source in pool:
            mappings,reasons=assignments(graph,node,source)
            for mapping in mappings:
                m=bind(source,mapping);m['id']=node['id'];m['variant_id']=node['id']+'/'+source['variant_id']+'/'+','.join(p+'='+e for p,e in sorted(mapping.items()))
                m['spec']=copy.deepcopy(m['spec']);m['spec'].update(id='graph-demand/'+node['id'],node_id=node['id'],node=copy.deepcopy(node),placement=[0,0])
                m['spec']['design_contract']=dict(input_node=node['id'],required_pairs=sorted(map(list,required_pairs(graph,node['id'])[1])),map_added_platforms=0)
                values.append(m)
            audit.append(dict(node=node['id'],source_version=source['source_version'],variant=source['variant_id'],matches=len(mappings),reasons=reasons))
        domains[node['id']]=values
    return domains,audit
