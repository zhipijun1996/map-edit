"""Compose a demanded multi-Port Macro using the existing exact CSP/assembler.

This searches only inside one Macro. It never constructs a regional graph.
"""
import copy,itertools
from .branch_terraces import terrace,ordered
from pcg.map_directed.content_domains.build import rename
from pcg.map_directed.shape_search.search import search,translated
from pcg.map_directed.direct_join.assemble import assemble_modules
from pcg.map_directed.catalog_feed.adapt import target
from pcg.map_directed.block_grid.contracts import declare,regions,raster,validate,connected
from pcg.map_directed.content_domains.reservation import connect
from ..factory.core.quality import digest


def trees(count):
    for code in itertools.product(range(count),repeat=max(0,count-2)):
        degree=[1+code.count(i)for i in range(count)];edges=[]
        for parent in code:
            leaf=next(i for i in range(count)if degree[i]==1);edges.append((leaf,parent));degree[leaf]-=1;degree[parent]-=1
        left=[i for i,d in enumerate(degree)if d==1];edges.append(tuple(left));yield edges


def payload(g,modules):
    c=assemble_modules(g,modules,[dict(id=e['id'],kind='side')for e in g['edges']]);owners={m['id']:m for m in modules};internal={e['id']for e in g['edges']};ports={};locations={}
    for m in modules:
        for key,raw in m['ports'].items():
            if key in internal:continue
            p=copy.deepcopy(raw);dx,dy=m['spec']['placement'];p['position']=[p['position'][0]+dx,p['position'][1]+dy];p['aperture']=translated(p['aperture'],[dx,dy]);p['grid']['cell']=[p['grid']['cell'][0]+round(dx/128),p['grid']['cell'][1]+round(dy/128)]
            pos=[raw['dock']['position'][0]+dx,raw['dock']['position'][1]+dy];p['dock']=target(c['case'],pos,key+'/staging');ports[key]=p;locations[key]=m['id']
    adj={k:[]for k in owners}
    for e in g['edges']:adj[e['from']].append((e['to'],e['id']));adj[e['to']].append((e['from'],e['id']))
    matrix={}
    for a,b in itertools.permutations(ports,2):
        start,end=locations[a],locations[b];queue=[(start,[])];seen={start};path=None
        while queue:
            k,steps=queue.pop(0)
            if k==end:path=steps;break
            for peer,eid in adj[k]:
                if peer not in seen:seen.add(peer);queue.append((peer,steps+[(k,peer,eid)]))
        program=[];incoming=a;current=start
        for fr,to,eid in path:
            program+=copy.deepcopy(c['nodes'][fr]['port_transitions'][incoming+'>'+eid]);e=c['edges'][eid];program+=copy.deepcopy(e['forward_waypoints']if e['from']==fr else e['reverse_waypoints']);incoming=eid;current=to
        program+=copy.deepcopy(c['nodes'][current]['port_transitions'][incoming+'>'+b]);matrix[a+'>'+b]=program
    first=next(iter(ports));case=copy.deepcopy(c['case']);case.update(id='compound-terrace-'+str(len(ports)),family='compound_terrace',ports=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in ports.items()])
    clearance=[translated(r,m['spec']['placement'])for m in modules for r in m['action_clearance']]
    x=min(r[0]for r in case['platforms']);y=min(r[1]for r in case['platforms']);right=max(r[0]+r[2]for r in case['platforms']);bottom=max(r[1]+r[3]for r in case['platforms'])
    m=dict(id=case['id'],variant_id=case['id'],case=case,ports=ports,center=copy.deepcopy(ports[first]['dock']),center_port=first,port_transitions=matrix,center_to_port={},port_to_center={},core=None,core_visit_program=[],boundary_gates=[],action_clearance=clearance,
        functional_roles=['junction','fork','merge','open_space'],selection_family='compound_terrace',motion_contract=copy.deepcopy(modules[0]['motion_contract']),spec=dict(id='module-demand/'+case['id'],node_id=case['id'],node=dict(id=case['id'],role='hub'),placement=[0,0],boundary_policy='open',space=dict(core_bounds=[x,y,right-x,bottom-y]),ports=list(ports.values())),
        adaptation=dict(new_geometry=True,source_physics_inherited=False,local_component_graph=g,components=[dict(id=v['id'],version=v['content_version'],placement=v['spec']['placement'])for v in modules]),
        content_components=[dict(source_version=v['source_version'])for v in modules],source_shape_sha256=digest(case['platforms']))
    cells=set().union(*(raster(r)for r in regions(m)))
    if not connected(cells):cells,extra=connect(cells,ports);m['adaptation']['explicit_empty_reservations']=extra
    m=declare(m,cells);errors=validate(m)
    if errors:raise ValueError(','.join(errors))
    m['content_version']='sha256:'+digest(dict(case=case,ports=ports,matrix=matrix));m['source_version']=m['content_version'];return m


def compact_clearance(module,step=8):
    m=copy.deepcopy(module);cells=set().union(*(raster(r,step)for r in m['action_clearance']));rows={}
    for x,y in cells:rows.setdefault(y,[]).append(x)
    rects=[];active={}
    for y in sorted(rows):
        spans=[]
        for x in sorted(rows[y]):
            if spans and x==spans[-1][1]:spans[-1][1]+=1
            else:spans.append([x,x+1])
        new={}
        for a,b in spans:
            key=(a,b);r=active.get(key)
            if r is not None and r[1]+r[3]==y*step:r[3]+=step
            else:r=[a*step,y*step,(b-a)*step,step];rects.append(r)
            new[key]=r
        active=new
    m['action_clearance']=rects;m['adaptation']['internal_search_clearance']='Conservative union of actual body samples rasterized at8px; never invents open action space';return m


def generate(port_count,seed,budget=12000,sources=None):
    if port_count not in [4,5,6]:raise ValueError('compound_port_count_outside_4_6')
    count=port_count-2;attempts=[]
    if sources:
        from pcg.map_directed.content_domains.build import load
        pool,_=load(sources);base=[compact_clearance(m)for m in pool if len(m['ports'])==3 and all(a+'>'+b in m.get('port_transitions',{})for a,b in itertools.permutations(m['ports'],2))and not m['case'].get('reward_sites')]
    else:base=[ordered(terrace(span,rise,drop))for span,rise,drop in itertools.product([512,640],[128,256],[128,256])]
    if not base:raise ValueError('verified_bidirectional_component_library_empty')
    for index,pairs in enumerate(trees(count)):
        g=dict(entry='c0',goal='c'+str(count-1),initial_abilities=['move','jump','shot_recoil'],nodes=[dict(id='c'+str(i))for i in range(count)],edges=[dict(id='i'+str(i),**{'from':'c'+str(a),'to':'c'+str(b)},bidirectional=True)for i,(a,b)in enumerate(pairs)],source='Demanded local compound Macro; no region topology')
        domains={}
        for node in g['nodes']:
            es=[e['id']for e in g['edges']if node['id']in [e['from'],e['to']]];values=[]
            for raw in base:
                for assigned in itertools.permutations(raw['ports'],len(es)):
                    mapping=dict(zip(assigned,es));mapping.update({p:'x'+node['id']+'-'+p for p in raw['ports']if p not in assigned});v=rename(raw,mapping);v['id']=node['id'];v['spec']['node_id']=node['id'];v['variant_id']=node['id']+'/'+raw['variant_id']+'/'+','.join(assigned);values.append(v)
            domains[node['id']]=values
        accepted={};failures=[]
        def outer_interface_check(ms):
            try:accepted['module']=payload(g,ms);return True
            except ValueError as e:
                if len(failures)<8:failures.append(str(e))
                return False
        r=search(g,domains,seed+'/'+str(index),budget=budget,require_blocks=True,allow_shared_air=True,solution_check=outer_interface_check);ms=r.pop('modules',[]);attempts.append(dict(status=r['status'],expanded=r['expanded'],external_interface_rejections=failures))
        if ms:
            m=accepted['module']
            m['adaptation']['local_search_attempts']=attempts;return m
    raise ValueError('compound_shape_unsatisfied/'+str(attempts))
