import copy,json,random,math,itertools
from .catalog import load
from .adapt import exterior,target
from .native import gate_join,deep_fork
from ..shape_search.search import search
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from ..director import REPO
from ..run import write

def rename(m,mapping):
    m=copy.deepcopy(m)
    for key in ['ports','center_to_port','port_to_center']:
        m[key]={mapping[k]:v for k,v in m[key].items()if k in mapping}
    for k,p in m['ports'].items():p['id']=k
    m['spec']['ports']=list(m['ports'].values());return m

def shared_high(fm,first):
    """A's upper port is a landing, not a horizontal corridor mouth."""
    p=fm['ports']['C'];index=p['dock']['support_indices'][0];r=fm['case']['platforms'][index]
    x=round(p['dock']['position'][0]/8)*8;y=p['position'][1]
    p.update(position=[x,y],aperture=[x-48,y-64,96,128],normal=[0,-1],kind='vertical',shared_landing_index=index,dock=target(fm['case'],[x,y],fm['id']+'/shared-high'))
    fm['center_to_port']['C'][-1]['target']=copy.deepcopy(p['dock'])
    center=first['center']['position'];entry=[round(center[0]/8)*8,center[1]];j=first['center']['support_indices'][0];dx=entry[0]-x;dy=entry[1]-y
    first['case']['platforms'][j]=[r[0]+dx,r[1]+dy,r[2],r[3]]
    if j not in first['case']['one_way_platform_indices']:first['case']['one_way_platform_indices'].append(j)
    q=first['ports']['in'];q.update(position=entry[:],aperture=[entry[0]-48,entry[1]-64,96,128],normal=[0,1],kind='vertical',shared_landing_index=j,dock=target(first['case'],entry,first['id']+'/shared-in'))
    from .adapt import samples
    bank=first['case']['platforms'][j]
    for f in samples()[(first['source_version'],first['case']['id'])]:
        if not f['grounded']:break
        if f['x']-12<bank[0]or f['x']+12>bank[0]+bank[2]:raise ValueError('shared_landing_too_short_for_source_takeoff')
    for other in first['ports'].values():target(first['case'],other['dock']['position'],'shared_landing_port_support')
    for actor in first['case'].get('enemies',[]):
        if actor['position'][1]<bank[1]and not bank[0]<=actor['position'][0]<=bank[0]+bank[2]:raise ValueError('shared_landing_loses_source_enemy_support')
    first['adaptation']['shared_entry_bank']=dict(source_fork=fm['source_version'],rect=first['case']['platforms'][j],status='New source-owned landing; continuous whole-map verification required')
    return first

def generate(out,seed):
    items=load();eligible=[x for x in items if x['row']['selected_for_plains_candidates']and len(x['cases'])==1]
    fork=next(x for x in items if x['record']['contentVersion'].startswith('sha256:e90dfa'))
    macros=[x for x in items if x['row']['family']=='gate-brake-return']
    rng=random.Random(seed);rng.shuffle(eligible);attempts=[];cache={}
    def candidate(x,pad):
        k=(x['record']['contentVersion'],pad)
        if k not in cache:
            try:cache[k]=exterior(x,'catalog-template',pad)
            except ValueError as e:cache[k]=ValueError(str(e))
        if isinstance(cache[k],ValueError):raise cache[k]
        return copy.deepcopy(cache[k])
    pair_cache={}
    def pair_ok(x,pad,jm,side):
        ck=(x['record']['contentVersion'],pad,jm['source_version'],side)
        if ck in pair_cache:return pair_cache[ck]
        try:m=candidate(x,pad)
        except ValueError:pair_cache[ck]=False;return False
        if side=='hi':
            for i in set(m['center']['support_indices'])|set(m['ports']['out']['dock']['support_indices']):m['case']['platforms'][i][3]=min(m['case']['platforms'][i][3],64)
        m['id']='T';p=copy.deepcopy(jm);p['id']='J';m=rename(m,{'out':'link'});p=rename(p,{side:'link'})
        g=dict(nodes=[dict(id='T'),dict(id='J')],edges=[dict(id='link',**{'from':'T','to':'J'})])
        result=search(g,{'T':[m],'J':[p]},'pair',budget=4)['status']=='feasible';pair_cache[ck]=result;return result
    for attempt in range(3):
        nodes=[];edges=[];domains={};assignments={};branches={};used=set()
        def edge(a,b,label):
            edges.append(dict(id=label,**{'from':a,'to':b},bidirectional=False,requires=[],switch=None,cost=1));return label
        for s in range(2):
            F='F'+str(s);J='J'+str(s);nodes.extend([dict(id=F,role='junction',label='反冲高低分流'),dict(id=J,role='junction',label='岩体汇合')])
            jm=gate_join(macros[s],J);drop=int(jm['ports']['lo']['position'][1]-jm['ports']['hi']['position'][1]-300)
            fm=exterior(deep_fork(fork,drop),F,0,True);pool=eligible[:];rng.shuffle(pool);pool.sort(key=lambda x:(x['record']['contentVersion']in used,x['row'].get('publication_batch')!='plains50-v1'));buckets={};groups=None
            numeric={};shared_ok=set();lower_ok=set();hi_last={};lo_last={}
            for x in pool:
                key=x['record']['contentVersion']
                try:
                    v=candidate(x,0);w=candidate(x,256)
                    numeric[key]=dict(lo=v['ports']['out']['position'][0]-v['ports']['in']['position'][0],hi=w['ports']['out']['position'][0]-w['ports']['in']['position'][0],shared_lo=v['ports']['out']['position'][0]-round(v['center']['position'][0]/8)*8,shared_hi=w['ports']['out']['position'][0]-round(w['center']['position'][0]/8)*8)
                    solids=v['case']['platforms']+[l['gate']for l in v['case']['latches']if not l.get('ferry_id')]
                    if v['center']['position'][1]-min(r[1]for r in solids)<=drop+210:lower_ok.add(key)
                    try:shared_high(copy.deepcopy(fm),v);shared_ok.add(key)
                    except ValueError:pass
                    for side,store in [('hi',hi_last),('lo',lo_last)]:
                        valid=[p for p in range(0,257,16)if pair_ok(x,p,jm,side)]
                        if valid:store[key]=valid
                except ValueError:continue
            pool=[x for x in pool if x['record']['contentVersion']in numeric]
            for triple in itertools.combinations(pool,3):
                if len({x['row']['family']for x in triple})<3:continue
                dy=sum(x['cases'][0]['exit_port'][1]-x['cases'][0]['entry_port'][1]for x in triple);buckets.setdefault(round(dy,3),[]).append(triple)
            span_cache={}
            keys=list(buckets);rng.shuffle(keys);keys.sort(key=abs)
            # Match vertical displacement before the same existing CSP solves
            # real shapes and horizontal closure. No fixed flat-lane filter.
            for dy in keys:
                ts=buckets[dy];rng.shuffle(ts)
                for a0 in ts:
                    a=next((list(p)for p in itertools.permutations(a0)if p[0]['record']['contentVersion']in shared_ok and p[-1]['record']['contentVersion']in hi_last),None)
                    if not a:continue
                    av={x['record']['contentVersion']for x in a}
                    for b0 in ts:
                        b=next((list(p)for p in itertools.permutations(b0)if p[-1]['record']['contentVersion']in lo_last),None)
                        if not b:continue
                        if av&{x['record']['contentVersion']for x in b}:continue
                        if len({x['row']['family']for x in a+list(b)})<4:continue
                        gap=fm['ports']['B']['position'][1]-fm['ports']['C']['position'][1]
                        safe_profile=True
                        for upper,lower in zip(a,b):
                            gap+=(lower['cases'][0]['exit_port'][1]-lower['cases'][0]['entry_port'][1])-(upper['cases'][0]['exit_port'][1]-upper['cases'][0]['entry_port'][1])
                            if gap<300:safe_profile=False;break
                        if not safe_profile:continue
                        try:
                            if not all(x['record']['contentVersion']in lower_ok for x in b):continue
                            def span(x,p,shared=False,side=None):
                                key=x['record']['contentVersion']
                                if side:
                                    ck=(key,side)
                                    if ck not in span_cache:
                                        ps=(hi_last if side=='hi'else lo_last)[key];vals=[]
                                        for q in ps:
                                            cm=candidate(x,q);vals.append(cm['ports']['out']['position'][0]-cm['ports']['in']['position'][0])
                                        span_cache[ck]=(min(vals),max(vals))
                                    return span_cache[ck][0 if p==0 else 1]
                                return numeric[key][('shared_'if shared else'')+('lo'if p==0 else'hi')]
                            amin=sum(span(x,0,i==0,'hi'if i==2 else None)for i,x in enumerate(a));amax=sum(span(x,256,i==0,'hi'if i==2 else None)for i,x in enumerate(a));bmin=sum(span(x,0,False,'lo'if i==2 else None)for i,x in enumerate(b));bmax=sum(span(x,256,False,'lo'if i==2 else None)for i,x in enumerate(b))
                        except ValueError:continue
                        offset=fm['ports']['B']['position'][0]-round(fm['ports']['C']['dock']['position'][0]/8)*8+jm['ports']['hi']['position'][0]-jm['ports']['lo']['position'][0]
                        if amin-bmax<=offset<=amax-bmin:groups=[list(a),list(b)];break
                    if groups:break
                if groups:break
            if not groups:raise ValueError('no_disjoint_vertical_and_span_compatible_branch_pair')
            used.update(x['record']['contentVersion']for group in groups for x in group)
            fmap={};jmap={}
            for side,group in zip(['hi','lo'],groups):
                chain=[F]+[f'{side}{s}-{i}'for i in range(3)]+[J];labels=[edge(a,b,f'{s}-{side}-{i}')for i,(a,b)in enumerate(zip(chain,chain[1:]))];branches[f'{s}/{side}']=chain
                fmap['C'if side=='hi'else'B']=labels[0];jmap[side]=labels[-1]
                for i,x in enumerate(group):
                    key=chain[i+1];nodes.append(dict(id=key,role='challenge',label=x['title']));assignments[key]=x['record']['contentVersion']
                    domains[key]=[]
                    for pad in range(0,257,1 if side=='lo'and i==2 else 16):
                        if i==2 and not pair_ok(x,pad,jm,side):continue
                        try:
                            m=candidate(x,pad);m['id']=key;m['spec']['id']='catalog-feed/'+key;m['spec']['node']['id']=key;m['variant_id']=key+'/'+x['record']['contentVersion'][7:15]+'/'+str(pad)
                        except ValueError:continue
                        if side=='hi'and i==0:m=shared_high(fm,m)
                        if side=='hi':
                            banks=set(m['center']['support_indices'])|set(m['ports']['out']['dock']['support_indices'])
                            for index in banks:m['case']['platforms'][index][3]=min(m['case']['platforms'][index][3],64)
                            m['adaptation']['upper_shore_max_root_depth']=64
                            m['content_version']='sha256:'+__import__('pcg.prototype.factory.core.quality',fromlist=['digest']).digest(dict(case=m['case'],ports=m['ports']))
                        domains[key].append(rename(m,{'in':labels[i],'out':labels[i+1]}))
            if s==0:jmap['out']=edge(J,'F1','between')
            else:
                # Third output is unused at the final exit. No fake reverse path.
                pass
            if s==1:fmap['in']='between'
            domains[F]=[rename(fm,fmap)];domains[J]=[rename(jm,jmap)]
        for n in nodes:n.update(grants=[],opens=[],reward=0)
        graph=dict(schema='map-notes/exploration-graph/v1',region='plains',seed=seed,entry='F0',goal='J1',initial_abilities=['move','jump','shot_recoil'],nodes=nodes,edges=edges)
        r=search(graph,domains,seed+'/'+str(attempt),budget=50000);modules=r.pop('modules',[]);attempts.append(r);write(out/'search-attempts.json',attempts)
        if not modules:continue
        for m in modules:
            c=m['case'];c.setdefault('source_case_binding',dict(id=c.get('id'),module_sha256=c.get('module_sha256'),contentVersion=m['source_version']))
            for k in ['factory_evidence','recorded_frames','validation_summary','module_sha256','factory_id']:c.pop(k,None)
            m['source_shape_sha256']=__import__('pcg.prototype.factory.core.quality',fromlist=['digest']).digest(c['platforms'])
            m['content_version']='sha256:'+__import__('pcg.prototype.factory.core.quality',fromlist=['digest']).digest(dict(case=c,ports=m['ports']))
        write(out/'precanonical.json',dict(graph=graph,modules=modules));modules=export_reload(modules,out/'module-library',producer='pcg/map_directed/catalog_feed/adapt.py')
        c=assemble_modules(graph,modules,[dict(id=e['id'],kind=next(m for m in modules if m['id']==e['from'])['ports'][e['id']]['kind'])for e in edges]);c.update(shop={},unresolved_rewards=[]);write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c))
        write(out/'selection.json',dict(source_library_versions=len(items),plains_selected=sum(x['row']['selected_for_plains_candidates']for x in items),interfaces_considered=len(eligible),latest_selected_versions=sorted(set(assignments.values())|{fork['record']['contentVersion']}|{x['record']['contentVersion']for x in macros}),assignments=assignments,branches=branches,legacy_structural_junctions=0,added_map_geometry=0,arbitrary_reverse_routes='UNKNOWN; no reverse inference',junction_design='Experimental concrete placement only; no multiport design approval inferred'))
        return c,branches
    raise ValueError('bounded_library_geometry_search_unsatisfied')

def cases_for(c,branches):
    from ..region_scale.materialize import case_for
    from ..r2_full.orchestrate import logical_route
    import itertools
    cases=[]
    for a,b in itertools.product(['lo','hi'],repeat=2):
        route=branches['0/'+a]+branches['1/'+b];v=case_for(c,logical_route(c,route),a+'-'+b)
        # Source-owned rewards are original Workshop services, not R2 invented nodes.
        v.update(extra_script=str(REPO/'pcg/map_directed/catalog_feed/extra.gd'),map_seed=c['exploration_graph']['seed'],formal_style_v2=True,title='风铃平原 · 最新内容库双分流整图',required_reward_ids=[])
        v['presentation_areas']=[dict(id=k,identity='windmill_plateau'if k.startswith('J')else'repair_gallery',position=n['center']['position'])for k,n in c['nodes'].items()]
        v['presentation_keep_clear']=[[r[0]+m['spec']['placement'][0],r[1]+m['spec']['placement'][1],r[2],r[3]]for m in c['modules']for r in m['action_clearance']]
        for leg in v['pilot_program']:
            if leg['kind']=='module':leg['entry']=dict(grounded=True,required_air_shots=1,maximum_shot_cooldown=0)
        cases.append(v)
    return cases
