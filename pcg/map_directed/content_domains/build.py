"""Shared catalog qualification and Port renaming; no topology generator."""
import copy,json
from .probe import cases as source_cases
from ..director import REPO
from ..block_grid.build import traces
from ..block_grid.contracts import declare,regions,raster,validate,connected
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
        modules=json.loads((root/'modules.json').read_text());ownership=owned_results(modules,results);input_ownership=owned_results(modules,stored)
        for m in modules:
            rr=ownership[m['variant_id']]
            if not rr or any(c['id']not in results for c in input_ownership[m['variant_id']])or not all(r['ok']for r in rr):audit.append(dict(version=m['source_version'],variant=m['variant_id'],status='physics_failed_or_incomplete'));continue
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


def rename(m,mapping):
    m=copy.deepcopy(m)
    for name in ['ports','port_to_center','center_to_port']:m[name]={mapping[k]:v for k,v in m.get(name,{}).items()if k in mapping}
    for k,p in m['ports'].items():p['id']=k
    for name in ['port_transitions','transition_options','transition_sources']:
        m[name]={mapping[a]+'>'+mapping[b]:v for key,v in m.get(name,{}).items()for a,b in[key.split('>')]if a in mapping and b in mapping}
    if m.get('center_port'):m['center_port']=mapping[m['center_port']]
    m['block_grid']['port_bindings']=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()];m['spec']['ports']=list(m['ports'].values());return m
