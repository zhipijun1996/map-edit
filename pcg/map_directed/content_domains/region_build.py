"""Folded 43-node exploration graph, real candidate domains and Block CSP."""
import copy
from .build import load,rename,tags
from .seam_probe import aperture
from ..director import regional
from ..run import write
from ..shape_search.search import search,translated
from ..direct_join.canonical import export_reload
from ..direct_join.assemble import assemble_modules
from ..direct_join.audit import audit
from pcg.prototype.factory.core.quality import digest


def graph(seed,stages=5):
    nodes=[];edges=[];plans=[];branches=[]
    def node(k,role,stage,slot=None):nodes.append(dict(id=k,role=role,stage=stage,slot=slot,label=k,grants=[],opens=[],reward=0,risk=2 if role=='reward'else 1))
    def edge(a,b,bidir,purpose):
        k='e'+str(len(edges));edges.append(dict(id=k,**{'from':a,'to':b},bidirectional=bidir,purpose=purpose,cost=1,requires=[],switch=None));return k
    for s in range(stages):
        f,j='F'+str(s),'J'+str(s);node(f,'junction',s);node(j,'merge',s)
        upper=[f'U{s}-{i}'for i in range(3)];lower=[f'L{s}-{i}'for i in range(3)]
        for i,k in enumerate(upper):node(k,'challenge',s,'upper-'+str(i))
        for i,k in enumerate(lower):node(k,'challenge',s,'lower-'+str(i))
        for label,path,bidir in [('upper',[f]+upper+[j],False),('lower',[f]+lower+[j],True)]:
            for a,b in zip(path,path[1:]):edge(a,b,bidir,label+'_main')
        branch=None
        if s%2==0:
            branch='R'+str(s);node(branch,'reward',s);edge(f,branch,True,'reward_foldback');branches.append(dict(id='cache-'+str(s),entry=f,rejoin=f,nodes=[branch],reward=branch,kind='foldback'))
        plans.append(dict(stage=s,fork=f,merge=j,upper=[f]+upper+[j],lower=[f]+lower+[j],reward=branch,direction=1 if s%2==0 else-1))
        if s:edge('J'+str(s-1),f,False,'region_drop')
    g=dict(schema='map-notes/exploration-graph/v1',seed=seed,region='plains',entry='F0',goal='J'+str(stages-1),initial_abilities=['move','jump','shot_recoil'],nodes=nodes,edges=edges,branches=branches,stages=plans,
           principal_routes=[dict(id='upper',nodes=[k for p in plans for k in p['upper']]),dict(id='lower',nodes=[k for p in plans for k in p['lower']])],
           source='PR #1 exploration contract, full-library domains; folded region with exact Block joins',mission_policy=dict(goal_kind='regional_exit_no_boss_encounter',stage_connections='one-way drops; within-stage return and reward foldback verified separately'))
    errors,_=regional.base.validate_graph(g)
    if errors:raise ValueError(errors)
    return g


def build(out,seed,sources,stages=5):
    g=graph(seed,stages);write(out/'exploration.json',g);pool,qualification=load(sources);write(out/'source-qualification.json',qualification);domains={};log=[]
    for n in g['nodes']:
        k=n['id'];s=n['stage'];plan=g['stages'][s];es=[e for e in g['edges']if k in[e['from'],e['to']]];values=[]
        for raw in pool:
            maps=[];ports=raw['ports'];star=not raw.get('port_transitions');role=n['role']
            if role=='junction'and star and 'ingress'in ports and 'upper'in ports and 'lower'in ports:
                if ('reward'in ports)!=bool(plan['reward']):continue
                if ports['upper']['normal']!=[plan['direction'],0]or ports['ingress']['position'][1]!=-896:continue
                m={}
                for e in es:
                    if e['purpose']=='region_drop':p='ingress'
                    elif e['purpose']=='reward_foldback':p='reward'
                    else:p=e['purpose'].split('_')[0]
                    m[p]=e['id']
                if s==0:m['ingress']='external-region-entry'
                maps=[m]
            elif role=='merge'and star and len(ports)==3 and set(ports)=={'upper','lower','onward'}:
                if ports['upper']['normal']!=[-plan['direction'],0]:continue
                m={}
                for e in es:m['onward'if e['purpose']=='region_drop'else e['purpose'].split('_')[0]]=e['id']
                if s==stages-1:m['onward']='external-region-exit'
                maps=[m]
            elif role=='reward'and len(ports)==1 and raw['case'].get('reward_sites'):
                p=next(iter(ports))
                if p+'>'+p in raw.get('port_transitions',{}):maps=[{p:es[0]['id']}]
            elif role=='challenge'and len(ports)==2:
                incoming=next(e['id']for e in es if e['to']==k);outgoing=next(e['id']for e in es if e['from']==k);lower=n['slot'].startswith('lower');index=int(n['slot'][-1])
                for pair in raw.get('port_transitions',{}):
                    a,b=pair.split('>');dy=ports[b]['position'][1]-ports[a]['position'][1];features=tags(raw,pair)
                    if a==b or ports[a]['normal']!=[-plan['direction'],0]or ports[b]['normal']!=[plan['direction'],0]:continue
                    if raw['case']['capabilities']!=g['initial_abilities']or raw['case'].get('expected_reward')not in [None,0]:continue
                    if raw['case'].get('moving_platforms'):continue
                    # The previous folded shelf bounds available headroom.
                    # Query geometry, never a family-name allowlist.
                    if s>0:
                        from ..block_grid.contracts import regions
                        highest=min(r[1]for r in regions(raw))
                        if ports[a]['dock']['position'][1]-highest>512:continue
                    if lower:
                        if dy!=0 or b+'>'+a not in raw['port_transitions']or 'air_shot'not in features:continue
                    else:
                        if dy not in [-128,0,128]:continue
                        if index==0 and('air_shot'not in features or dy!=(-128 if s%2==0 else 0)):continue
                        if index==1 and('hazard_precision'not in features or dy<0):continue
                        if index==2 and not({'air_shot','descent'}&features):continue
                        if s%2==1 and index==2 and dy!=-128:continue
                    maps.append({a:incoming,b:outgoing})
            for mapping in maps:
                m=rename(aperture(raw),mapping);m['id']=k;m['spec'].update(id='region-demand/'+k,node_id=k,node=copy.deepcopy(n),design_contract=dict(block_size=128,slot=n['slot'],roles=[role],map_added_platforms=0,whole_map_verification_required=True))
                if role!='reward':m['adaptation']['reward_allocation']=dict(source_sites=copy.deepcopy(m['case'].get('reward_sites',[])),request=0);m['case']['reward_sites']=[]
                m['variant_id']=k+'/'+raw['variant_id'];m['content_components']=[dict(source_version=raw['source_version'],run=raw['independent_evidence']['run'])];values.append(m)
            log.append(dict(node=k,source_version=raw['source_version'],variant=raw['variant_id'],matches=len(maps)))
        domains[k]=values
    write(out/'match-audit.json',log);write(out/'candidate-domain-counts.json',{k:len(v)for k,v in domains.items()});write(out/'challenge-specifications.json',[m[0]['spec']for m in domains.values()if m]);attempts=[];best=None
    if all(domains.values()):
        for i in range(8):
            r=search(g,domains,seed+'/fold-'+str(i),budget=120000,require_blocks=True,allow_shared_air=True);ms=r.pop('modules',[]);attempts.append(r);write(out/'search-attempts.json',attempts)
            if ms:
                # Avoid a completely flat upper arm, even when closure allows it.
                upper_changes=[sum(abs(m['ports'][next(e['id']for e in g['edges']if e['from']==m['id'])]['position'][1]-m['ports'][next(e['id']for e in g['edges']if e['to']==m['id'])]['position'][1])for m in ms if m['id']in p['upper'][1:-1])for p in g['stages']]
                if any(v==0 for v in upper_changes):attempts[-1]['design_rejection']='flat_upper_arm';continue
                best=(i,ms);break
    if not best:write(out/'generator-feedback.json',dict(status='unsatisfied',empty_domains=[k for k,v in domains.items()if not v],required_nodes=len(g['nodes']),preserved_edges=len(g['edges']),no_platform_fallback=True));return None
    i,ms=best;write(out/'selected-search.json',dict(attempt=i,**attempts[i]));write(out/'precanonical.json',dict(graph=g,modules=ms));ms=export_reload(ms,out/'module-library',producer='pcg/map_directed/content_domains/region_build.py');c=assemble_modules(g,ms,[dict(id=e['id'],kind=next(m for m in ms if m['id']==e['from'])['ports'][e['id']]['kind'])for e in g['edges']]);c.update(shop={},unresolved_rewards=[])
    rects=[translated(r,m['spec']['placement'])for m in ms for r in m['action_clearance']+m['case']['platforms']]
    xs=[r[0]for r in rects];ys=[r[1]for r in rects];right=max(r[0]+r[2]for r in rects);bottom=max(r[1]+r[3]for r in rects);c['case']['world_bounds']=[min(xs)-128,min(ys)-128,right-min(xs)+256,bottom-min(ys)+256]
    write(out/'compiled.json',c);write(out/'assembly-audit.json',audit(c));write(out/'map-recipe.json',dict(seed=seed,graph_sha256=digest(g),modules=[m['canonical_document']for m in ms],block_origins={m['id']:m['spec']['block_placement']for m in ms},map_added_geometry=0))
    write(out/'content-allocation.json',[dict(node=m['id'],source_version=m['source_version'],family=m['selection_family'],native_pairs=list(m.get('port_transitions',{})),components=m['content_components'])for m in ms]);return c
