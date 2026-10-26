"""Joint integer-Block placement from full-library gameplay domains and matrices."""
import copy,json
from pathlib import Path
from .catalog import match
from .probe import cases as source_cases
from ..director import REPO,regional
from ..run import write
from ..block_grid.build import traces
from ..block_grid.contracts import declare,regions,raster,validate,connected
from ..shape_search.search import search
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from pcg.prototype.factory.core.quality import digest

def owned_results(modules,results):
    """A derived variant owns its cases, never its parent's prefix bucket."""
    keys=[m['variant_id']for m in modules]
    if len(keys)!=len(set(keys)):raise ValueError('duplicate_source_variant_identity')
    keys=sorted(keys,key=len,reverse=True);owned={k:[]for k in keys}
    for case_id,result in results.items():
        owner=next((k for k in keys if case_id.startswith(k+'/')),None)
        if owner is not None:owned[owner].append(result)
    return owned

def load(sources):
    pool=[];audit=[];seen=set()
    for path in sources:
        root=REPO/path;_,results=traces(root/'physics');original=json.loads((root/'cases.json').read_text())['cases'];stored={c['id']:c for c in original}
        if len(stored)!=len(original):raise ValueError('duplicate_source_case_identity')
        modules=json.loads((root/'modules.json').read_text());ownership=owned_results(modules,results)
        for m in modules:
            rr=ownership[m['variant_id']]
            if not rr or not all(r['ok']for r in rr):audit.append(dict(version=m['source_version'],variant=m['variant_id'],status='physics_failed_or_incomplete'));continue
            is_return=bool(m.get('adaptation',{}).get('return_proposal'))
            if not m.get('transition_options'):
                from .junction_probe import cases as junction_cases
                if any(c['id']not in stored or c!=stored[c['id']]for c in junction_cases(m)):raise ValueError('junction_or_scoped_input_drift/'+m['variant_id'])
            if m.get('transition_options')and not is_return:
                expected=source_cases(m)
                if any(c['id']not in stored or c!=stored[c['id']]for c in expected):raise ValueError('native_source_case_drift/'+m['variant_id'])
            if is_return and not any('continuous-roundtrip'in r['id']for r in rr):raise ValueError('same_world_return_proof_required')
            from .catalog import WORLD
            signature=digest(dict(source_version=m['source_version'],variant=m['variant_id'],world={k:m['case'].get(k,[])for k in WORLD},ports=m['ports'],transitions=m.get('port_transitions',{}),outbound=m.get('center_to_port')))
            if signature in seen:continue
            seen.add(signature);m=copy.deepcopy(m);frames=[f for r in rr for f in r['frames']];m['action_clearance']=[list(v)for v in dict.fromkeys((f['x']-12,f['y']-18,24,36)for f in frames[::2])]
            cells=set().union(*(raster(r)for r in regions(m)))
            cells.update(map(tuple,m.get('adaptation',{}).get('empty_reserved_blocks_added',[])))
            cells.update(map(tuple,m.get('adaptation',{}).get('explicit_empty_reservations',[])))
            forbidden={tuple(p['grid']['cell'][i]+p['normal'][i]for i in range(2))for p in m['ports'].values()}
            halo=set().union(*(raster([x-16,y-16,w+32,h+32])for x,y,w,h in m['action_clearance']))
            cells.update(halo-forbidden)
            m['adaptation']['trajectory_reservation_margin_pixels']=16
            if not connected(cells):
                from .reservation import connect
                try:cells,added=connect(cells,m['ports']);m['adaptation']['measured_empty_reservation_added']=added
                except ValueError as e:audit.append(dict(version=m['source_version'],variant=m['variant_id'],status='measured_reservation_unconnectable',errors=[str(e)]));continue
            m=declare(m,cells)
            errors=validate(m)
            if errors:audit.append(dict(version=m['source_version'],variant=m['variant_id'],status='measured_socket_or_shape_invalid',errors=errors));continue
            m['independent_evidence']=dict(run=path,case_ids=[r['id']for r in rr],scope='Exact finite native directions and same-world return where present; new Map verification mandatory',general_admission=False);m['source_shape_sha256']=digest(m['case']['platforms']);pool.append(m)
    return pool,audit

def tags(m,pair):
    result=set(m.get('transition_sources',{}).get(pair,{}).get('features',[]));ops=[op for leg in m.get('port_transitions',{}).get(pair,[])for op in leg.get('control_plan',[])]
    names={o['op']for o in ops}
    if 'jump'in names and 'shoot'in names:result.add('air_shot')
    if any(o.get('aim_cell',{}).get('kind')=='bell'for o in ops):result.add('shot_trigger')
    a,b=pair.split('>');dy=m['ports'][b]['position'][1]-m['ports'][a]['position'][1]
    if dy<=-96:result.add('ascent')
    if dy>=96:result.add('descent')
    if sum(o['op']=='shoot'for o in ops)>=2 and sum(o['op']=='jump'for o in ops)>=2 and any(o.get('trigger',{}).get('state')=='grounded'for o in ops):result.add('landing_reload')
    return result

def graph(seed):
    g=dict(seed=seed,entry='start',goal='merge',initial_abilities=['move','jump','shot_recoil'],region='plains',block_size=128,nodes=[],edges=[],branches=[],source='Full-library gameplay matching; native Port matrix; integer Block search')
    definitions=[('start','junction',[]),('upperA','challenge',['ascent','air_shot','shot_trigger']),('upperB','challenge',['descent','hazard_precision']),('lowerA','challenge',['air_shot','shot_trigger']),('lowerB','challenge',['landing_reload']),('merge','rest',[]),('reward','reward',['hazard_precision'])]
    for key,role,required in definitions:g['nodes'].append(dict(id=key,role=role,label=key,grants=[],opens=[],reward=0,risk=2 if role=='reward'else 1,required_features=required))
    def edge(a,b,bidir,purpose):g['edges'].append(dict(id='e'+str(len(g['edges'])),**{'from':a,'to':b},bidirectional=bidir,purpose=purpose,cost=1,requires=[],switch=None))
    edge('start','upperA',False,'upper_main');edge('upperA','upperB',False,'upper_main');edge('upperB','merge',False,'upper_main');edge('start','lowerA',True,'lower_main');edge('lowerA','lowerB',True,'lower_main');edge('lowerB','merge',True,'lower_main');edge('start','reward',True,'reward_foldback')
    g['principal_routes']=[dict(id='upper',nodes=['start','upperA','upperB','merge']),dict(id='lower',nodes=['start','lowerA','lowerB','merge'])];g['branches']=[dict(id='optional-cache',kind='foldback',entry='start',nodes=['reward'],reward='reward',rejoin='start')];return g

def rename(m,mapping):
    m=copy.deepcopy(m)
    for name in ['ports','port_to_center','center_to_port']:m[name]={mapping[k]:v for k,v in m.get(name,{}).items()if k in mapping}
    for k,p in m['ports'].items():p['id']=k
    for name in ['port_transitions','transition_options','transition_sources']:
        m[name]={mapping[a]+'>'+mapping[b]:v for key,v in m.get(name,{}).items()for a,b in[key.split('>')]if a in mapping and b in mapping}
    if m.get('center_port'):m['center_port']=mapping[m['center_port']]
    m['block_grid']['port_bindings']=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()];m['spec']['ports']=list(m['ports'].values());return m

def build(out,seed,sources):
    g=graph(seed);errors,logic=regional.base.validate_graph(g)
    if errors:raise ValueError(errors)
    write(out/'exploration.json',g);pool,source_audit=load(sources);write(out/'source-qualification.json',source_audit);domains={};matchlog=[]
    for n in g['nodes']:
        key=n['id'];edges=[e for e in g['edges']if key in[e['from'],e['to']]];values=[]
        for raw in pool:
            mappings=[];why=[];pair='';is_junction=not raw.get('port_transitions')
            if key=='start'and is_junction and len(raw['ports'])==3 and set(raw['ports'])=={'upper','lower','reward'}:mappings=[dict(upper='e0',lower='e3',reward='e6')]
            elif key=='merge'and is_junction and len(raw['ports'])==2 and set(raw['ports'])=={'upper','lower'}:mappings=[dict(upper='e2',lower='e5')]
            elif key=='reward'and len(raw['ports'])==1 and raw['case'].get('reward_sites')and raw['case'].get('thorns'):
                p=next(iter(raw['ports']))
                if p+'>'+p in raw.get('port_transitions',{}):mappings=[{p:'e6'}]
            elif key not in ['start','merge','reward']and len(raw['ports'])==2:
                incoming=next(e['id']for e in edges if e['to']==key);outgoing=next(e['id']for e in edges if e['from']==key);needs_return=all(e['bidirectional']for e in edges)
                for pair in raw.get('port_transitions',{}):
                    a,b=pair.split('>')
                    if a==b or not set(n['required_features'])<=tags(raw,pair):continue
                    if needs_return and b+'>'+a not in raw['port_transitions']:why.append('required_return_direction_missing');continue
                    if raw['case'].get('expected_reward')not in [None,0]:why.append('intrinsic_reward_budget_requires_retaining_source_rewards');continue
                    mappings.append({a:incoming,b:outgoing})
            else:why.append('role_or_port_count_mismatch')
            for mapping in mappings:
                m=rename(raw,mapping);m['id']=key;m['spec'].update(id='content-demand/'+key,node_id=key,node=copy.deepcopy(n),design_contract=dict(required_features=n['required_features'],port_count=len(edges),return_required=all(e['bidirectional']for e in edges),no_helper_platforms=True))
                if key not in ['reward']:m['adaptation']['reward_allocation']=dict(source_sites=copy.deepcopy(m['case'].get('reward_sites',[])),request=0,source_proof_not_inherited=True);m['case']['reward_sites']=[]
                m['variant_id']=key+'/'+raw['variant_id'];m['content_components']=[dict(source_version=raw['source_version'],features=n['required_features'],input_run=raw['independent_evidence']['run'])];values.append(m)
            matchlog.append(dict(node=key,source_version=raw['source_version'],variant=raw['variant_id'],matched=len(mappings),reasons=sorted(set(why))if not mappings else[]))
        domains[key]=values
    write(out/'match-audit.json',matchlog);write(out/'candidate-domain-counts.json',{k:len(v)for k,v in domains.items()});write(out/'challenge-specifications.json',[dict(node=n['id'],required_features=n['required_features'],edges=[e['id']for e in g['edges']if n['id']in[e['from'],e['to']]],block_size=128)for n in g['nodes']]);attempts=[];accepted=[]
    if all(domains.values()):
        for i in range(8):
            r=search(g,domains,seed+'/block-'+str(i),budget=24000,require_blocks=True);ms=r.pop('modules',[]);attempts.append(r)
            if ms:
                cells=r['block_origins'];box=(max(p[0]for p in cells.values())-min(p[0]for p in cells.values())+1)*(max(p[1]for p in cells.values())-min(p[1]for p in cells.values())+1);accepted.append((box,i,ms))
    write(out/'search-attempts.json',attempts)
    if not accepted:write(out/'generator-feedback.json',dict(status='needs_design',empty_domains=[k for k,v in domains.items()if not v],preserved_edges=[e['id']for e in g['edges']],may_add_connection_platforms=False,may_delete_required_routes=False,source_domains_are_full_library_queries=True));return None
    _,chosen,ms=min(accepted,key=lambda v:v[:2]);write(out/'selected-search.json',dict(attempt=chosen,**attempts[chosen]));write(out/'precanonical.json',dict(graph=g,modules=ms));ms=export_reload(ms,out/'module-library',producer='pcg/map_directed/content_domains/build.py');c=assemble_modules(g,ms,[dict(id=e['id'],kind='side')for e in g['edges']]);c.update(shop={},unresolved_rewards=[])
    if c['exploration_graph']!=g:raise ValueError('blueprint_changed_during_materialization')
    write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c));write(out/'map-recipe.json',dict(seed=seed,graph_sha256=digest(g),modules=[m['canonical_document']for m in ms],integer_block_origins={m['id']:m['spec']['block_placement']for m in ms},map_added_terrain=0))
    write(out/'content-allocation.json',[dict(node=m['id'],source_version=m['source_version'],family=m['selection_family'],ports=list(m['ports']),native_pairs=list(m.get('port_transitions',{})),thin_oneway_platforms=len(m['case']['one_way_platform_indices']),components=m['content_components'])for m in ms]);return c
