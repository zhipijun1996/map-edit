"""Read real Macro payloads; precompute finite source-owned shape variants.

Only the two quiet/rest banks vary. No action core is scaled, no solver is
allowed to synthesize floors, and no parent coordinates reach the searcher.
"""
import copy,gzip,json
from pathlib import Path
from ..director import REPO
from pcg.prototype.factory.core.engine import file_sha
from pcg.prototype.factory.core.quality import digest

def rect_bounds(rects):
    return [min(r[0]for r in rects),min(r[1]for r in rects),max(r[0]+r[2]for r in rects),max(r[1]+r[3]for r in rects)]

def observed_clearance(source,modules):
    """Actual body samples for existing module-action policies, not AABBs."""
    result={k:[]for k in modules};seen={k:set()for k in modules}
    for batch in json.loads((source/'physics/batches.json').read_text()):
        raw=gzip.decompress((source/'physics'/batch['gzip_path']).read_bytes())
        if __import__('hashlib').sha256(raw).hexdigest()!=batch['raw_output_sha256']:raise ValueError('source_physics_trace_drift')
        for r in json.loads(raw)['results']:
            if not r['ok']:continue
            frames={int(f['frame']):f for f in r['frames']}
            for leg in r['pilot']['legs']:
                if not leg.get('ok')or leg['kind']!='module':continue
                owner=str(leg['target']['id']).split('/')[0]
                if owner not in modules:continue
                dx,dy=modules[owner]['spec']['placement']
                for tick in range(int(leg['start']['frame']),int(leg['end']['frame'])+1,2):
                    if tick not in frames:continue
                    f=frames[tick];x=f['x']-dx;y=f['y']-dy
                    key=(round(x,1),round(y,1))
                    if key in seen[owner]:continue
                    seen[owner].add(key);result[owner].append([x-12,y-18,24,36])
    return result

def bank_variant(source,width,level):
    m=copy.deepcopy(source);key=m['id'];c=m['case'];oldw=m['spec']['space']['core_bounds'][2]
    if key=='lookout':
        indices=[10,11,12,13,14];oldlevel=60;start=330;original_end=400
    elif key=='hollow':
        indices=[10,11,12,13,14];oldlevel=100;start=390;original_end=590
    else:raise ValueError('unsupported_bank_variant')
    # The variation changes only a quiet terminal rock bank. It is authored
    # before search, and re-exported as a new canonical Module version.
    delta=level-oldlevel;scale=(width-start)/(original_end-start)
    for i in indices:
        p=c['platforms'][i];p[0]=start+(p[0]-start)*scale;p[2]*=scale;p[1]+=delta
    if key=='hollow':
        for saw in c['saws']:
            saw['origin'][0]=start+(saw['origin'][0]-start)*scale;saw['origin'][1]+=delta
    seen=set()
    def patch(v):
        if isinstance(v,dict):
            if id(v)in seen:return
            seen.add(id(v))
            if any(i in indices for i in v.get('support_indices',[])):
                x,y=v['position'];v['position']=[start+(x-start)*scale,y+delta]
                v['region']=[v['position'][0]-8,v['position'][1]-4,16,8]
            if v.get('target_x',-float('inf'))>=start:v['target_x']=start+(v['target_x']-start)*scale
            dynamic=v.get('trigger',{}).get('dynamic',{})
            if dynamic.get('kind')=='actor_x'and dynamic['value']>=start:dynamic['value']=start+(dynamic['value']-start)*scale
            for z in v.values():patch(z)
        elif isinstance(v,list):
            for z in v:patch(z)
    for k in ['ports','center','core','center_to_port','port_to_center','core_visit_program']:patch(m.get(k))
    right=next(p for p in m['ports'].values()if p['normal']==[1,0]);right['position']=[width,level];right['dock']['position']=[width-24,level];right['dock']['region']=[width-32,level-4,16,8]
    right['aperture']=[width-48,level-96,96,136];right['dock_world']=right['dock']['position'][:]
    m['spec']['space']['core_bounds'][2]=width
    # Explicit new input policies over the changed supports, not interpolation
    # of an old motion proof. Existing terrain ownership and cores are retained.
    def t(x,y,i,label):return dict(id=key+'/'+label,position=[x,y],region=[x-8,y-4,16,8],support_indices=[i],grounded=True)
    if key=='lookout':
        take=t(300,0,5,'variant-edge');dest=right['dock']
        m['center_to_port']['e2']=[dict(kind='walk',target=take),dict(kind='walk'if level==0 else'drop',target=dest)]
        m['port_to_center']['e2']=[dict(kind='jump',target=copy.deepcopy(m['center']),hold_ticks=20)]
    else:
        bank=t(start+(412-start)*scale,level,10,'variant-bank')
        # Keep the measured gear-phase policy. Only add the real ascent needed
        # when a selected bank rises above the previous standing level.
        if level<80:m['center_to_port']['e5'].insert(0,dict(kind='jump',target=bank,hold_ticks=20))
    return m

def remove_retired_travel_caps(m):
    """Old travel latches were removed; their unused sky caps are retired too."""
    if m['id']not in ['west','ridge']or m['case']['latches']:return m
    c=m['case'];removed={i for i,p in enumerate(c['platforms'])if p[1]<-100}
    used=set()
    def collect(v):
        if isinstance(v,dict):
            used.update(v.get('support_indices',[]))
            for z in v.values():collect(z)
        elif isinstance(v,list):
            for z in v:collect(z)
    for f in ['ports','core','center','center_to_port','port_to_center']:collect(m.get(f))
    if removed&used:raise ValueError('retired_cap_is_an_actual_route_support')
    mapping={i:i-sum(j<i for j in removed)for i in range(len(c['platforms']))if i not in removed}
    c['platforms']=[p for i,p in enumerate(c['platforms'])if i not in removed];c['one_way_platform_indices']=[mapping[i]for i in c['one_way_platform_indices']if i in mapping]
    seen=set()
    def patch(v):
        if isinstance(v,dict):
            if id(v)in seen:return
            seen.add(id(v))
            if 'support_indices'in v:v['support_indices']=[mapping[i]for i in v['support_indices']]
            if 'shared_landing_index'in v:v['shared_landing_index']=mapping[v['shared_landing_index']]
            for z in v.values():patch(z)
        elif isinstance(v,list):
            for z in v:patch(z)
    for f in ['ports','core','center','center_to_port','port_to_center','core_visit_program']:patch(m.get(f))
    m['retired_nonserving_cap_indices']=sorted(removed)
    return m

def reflect(m):
    m=copy.deepcopy(m);c=m['case'];W=m['spec']['space']['core_bounds'][2]
    def rect(r):return [W-r[0]-r[2],r[1],r[2],r[3]]
    c['platforms']=[rect(p)for p in c['platforms']];c['hazards']=[rect(p)for p in c.get('hazards',[])]
    for key in ['spawn','entry_port','exit_port']:
        if key in c:c[key][0]=W-c[key][0]
    if 'goal'in c:c['goal']=rect(c['goal'])
    for s in c['saws']:s['origin'][0]=W-s['origin'][0];s['travel'][0]*=-1
    for e in c['enemies']:e['position'][0]=W-e['position'][0]
    for l in c['latches']:
        l['bell'][0]=W-l['bell'][0];l['gate']=rect(l['gate'])
        if l.get('return_access'):l['return_access'][0]=W-l['return_access'][0]
    for s in c.get('shop_sites',[]):s['position'][0]=W-s['position'][0]
    for p in m['ports'].values():
        p['position'][0]=W-p['position'][0];p['normal'][0]*=-1;p['aperture']=rect(p['aperture'])
    seen=set()
    def patch(v):
        if isinstance(v,dict):
            if id(v)in seen:return
            seen.add(id(v))
            if 'support_indices'in v:
                v['position'][0]=W-v['position'][0];v['region']=rect(v['region'])
            if 'target_x'in v:v['target_x']=W-v['target_x']
            if v.get('op')=='axis':v['value']*=-1
            if 'direction'in v and isinstance(v['direction'],list):v['direction'][0]*=-1
            q=v.get('trigger',{}).get('dynamic',{})
            if q.get('kind')=='actor_x':q['value']=W-q['value'];q['direction']='lte'if q['direction']=='gte'else'gte'
            for z in v.values():patch(z)
        elif isinstance(v,list):
            for z in v:patch(z)
    for f in ['center','core','ports','center_to_port','port_to_center','core_visit_program']:patch(m.get(f))
    patch(c.get('reward_sites',[]))
    m['action_clearance']=[rect(r)for r in m['action_clearance']]
    return m

def load():
    protocol=json.loads(Path(__file__).with_name('protocol.json').read_text());source=REPO/protocol['source_catalog']
    compiled=json.loads((source/'compiled.json').read_text())
    from ..direct_join.canonical import reload_catalog
    loaded=reload_catalog(source/'module-library')
    if {m['id']:m['content_version']for m in loaded}!={m['id']:m['content_version']for m in compiled['modules']}:raise ValueError('canonical_parent_version_mismatch')
    by={m['id']:m for m in loaded}
    clearance=observed_clearance(source,by);domains={};v=protocol['variants'];excluded=[]
    for key,old in by.items():
        candidates=[old]
        if key in ['lookout','hollow']:
            candidates=[bank_variant(old,w,y)for w in v[key+'_widths']for y in v[key+'_exit_levels']]
        domains[key]=[]
        for ordinal,raw in enumerate(candidates):
            W,H=raw['spec']['space']['core_bounds'][2:]
            if any(s['origin'][0]-abs(s['travel'][0])-s['radius']<0 or s['origin'][0]+abs(s['travel'][0])+s['radius']>W or s['origin'][1]-abs(s['travel'][1])-s['radius']<0 or s['origin'][1]+abs(s['travel'][1])+s['radius']>H for s in raw['case']['saws']):
                excluded.append(dict(role=key,ordinal=ordinal,reason='dynamic_sweep_outside_declared_core'));continue
            raw=remove_retired_travel_caps(copy.deepcopy(raw));raw.pop('canonical_document',None);raw['action_clearance']=copy.deepcopy(clearance[key])
            for mirrored in [False,True]:
                m=reflect(raw)if mirrored else copy.deepcopy(raw)
                m['spec']['placement']=[0,0];m['spec']['id']='shape-search/'+key
                for p in m['ports'].values():p.pop('dock_world',None)
                m['spec']['ports']=copy.deepcopy(list(m['ports'].values()))
                m['variant_id']=key+'/'+str(ordinal)+('/mirror'if mirrored else'/original')
                m['source_template_version']=old['content_version'];m['variant_mirrored']=mirrored
                m['source_shape_sha256']=digest(m['case']['platforms'])
                m['content_version']='sha256:'+digest({k:m[k]for k in ['case','ports','core','boundary_gates']})
                m['motion_contract']={'mode':'grounded_dock','capabilities':['move','jump','shot_recoil'],'entry_grounded':True,
                    'required_air_shots':1,'maximum_entry_speed':1,'entry_cooldown':'must_recover_on_actual_bank',
                    'status':'isolated-policy-requirement; general relation UNKNOWN; fresh whole-map test required'}
                domains[key].append(m)
    return compiled['exploration_graph'],domains,dict(catalog=str(source.relative_to(REPO)),compiled_sha256=file_sha(source/'compiled.json'),
        source_positions_consumed_by_solver=False,body_half_extents=[12,18],clearance_source='real parent whole-map module-action trajectories, sampled every two ticks; not universal envelopes',
        excluded_variants=excluded,source_identity='fixed eight-role two-loop Mission/Exploration; no seed topology diversity claim')
