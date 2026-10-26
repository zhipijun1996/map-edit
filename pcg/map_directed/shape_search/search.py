"""Bounded CSP: actual port poses, collider unions and measured action space."""
import copy,random,time
from .catalog import rect_bounds
from pcg.prototype.factory.core.quality import digest

def translated(r,p):return [r[0]+p[0],r[1]+p[1],r[2],r[3]]
def intersects(a,b):return min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0])>.25 and min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1])>.25
def closed_solids(m):
    # Original ShotLatch.bind_motion_control disables its dummy gate collider.
    return m['case']['platforms']+[l['gate'] for l in m['case'].get('latches',[])if not l.get('ferry_id')]
def sweeps(m):
    result=[]
    for s in m['case'].get('saws',[]):
        x,y=s['origin'];tx,ty=s['travel'];r=s['radius'];result.append([x-abs(tx)-r,y-abs(ty)-r,2*(abs(tx)+r),2*(abs(ty)+r)])
    for platform in m['case'].get('moving_platforms',[]):
        a,b=platform['start'],platform['finish'];w,h=platform['size']
        result.append([min(a[0],b[0])-w/2,min(a[1],b[1])-h/2,abs(a[0]-b[0])+w,abs(a[1]-b[1])+h])
    return result
def compatible_state(a,b,abilities,state=None):
    state=state or dict(grounded=True,air_shots=1,speed=0)
    for m in [a,b]:
        c=m['motion_contract']
        if not set(c['capabilities'])<=set(abilities):return False
        if c['mode']!='grounded_dock'or c['entry_grounded']is not True:return False
        if not state.get('grounded')or state.get('air_shots',0)<c['required_air_shots']or state.get('speed',float('inf'))>c['maximum_entry_speed']:return False
    return True

def search(graph,domains,seed,mode='shape_action',budget=50000,abilities=None,entry_state=None):
    started=time.perf_counter();rng=random.Random(seed);abilities=abilities or ['move','jump','shot_recoil']
    adjacent={n['id']:[]for n in graph['nodes']}
    for e in graph['edges']:
        adjacent[e['from']].append((e,e['to']));adjacent[e['to']].append((e,e['from']))
    candidates={k:[m for m in v if compatible_state(m,m,abilities,entry_state)]for k,v in domains.items()}
    for values in candidates.values():rng.shuffle(values)
    selected={};positions={};expanded=0;rejects={};trace=[];examples=[]
    def reject(reason):rejects[reason]=rejects.get(reason,0)+1
    displacement_cache={}
    def remaining_chains_possible():
        # A chain between two placed anchors has a known remaining port delta.
        # Reject impossible intervals before enumerating every geometric pose.
        for anchor in selected:
            for first,neighbor in adjacent[anchor]:
                if neighbor in selected:continue
                key=neighbor;incoming=first;parts=[];seen=set()
                while key not in selected and len(adjacent[key])==2 and key not in seen:
                    seen.add(key);outgoing,peer=next((e,p)for e,p in adjacent[key]if e['id']!=incoming['id'])
                    ck=(key,incoming['id'],outgoing['id'])
                    if ck not in displacement_cache:
                        values=[[m['ports'][outgoing['id']]['position'][i]-m['ports'][incoming['id']]['position'][i]for i in range(2)]for m in candidates[key]]
                        if not values:return False
                        displacement_cache[ck]=([min(v[i]for v in values)for i in range(2)],[max(v[i]for v in values)for i in range(2)])
                    parts.append(displacement_cache[ck]);key=peer;incoming=outgoing
                if key in selected and parts:
                    a=selected[anchor]['ports'][first['id']]['position'];b=selected[key]['ports'][incoming['id']]['position']
                    desired=[positions[key][i]+b[i]-positions[anchor][i]-a[i]for i in range(2)]
                    if any(desired[i]<sum(p[0][i]for p in parts)-.01 or desired[i]>sum(p[1][i]for p in parts)+.01 for i in range(2)):return False
        return True
    local_cache={};pair_cache={}
    def local(m):
        k=id(m)
        if k not in local_cache:
            rects=closed_solids(m);dynamic=sweeps(m);clearance=m['action_clearance']
            a=rect_bounds(rects+dynamic+clearance)
            local_cache[k]=(rects,dynamic,clearance,[a[0],a[1],a[2]-a[0],a[3]-a[1]])
        return local_cache[k]
    def pair_reason(m,p,other,q):
        ours,md,mc,_=local(m);theirs0,od,oc,_=local(other)
        rects=[translated(r,p)for r in ours];theirs=[translated(r,q)for r in theirs0]
        if mode=='aabb':
            a=rect_bounds(rects);b=rect_bounds(theirs)
            return 'bounding_box_overlap'if intersects([a[0],a[1],a[2]-a[0],a[3]-a[1]],[b[0],b[1],b[2]-b[0],b[3]-b[1]])else None
        shared_ours=set();shared_theirs=set()
        for i,a in enumerate(rects):
            for j,b in enumerate(theirs):
                if not intersects(a,b):continue
                shared_a={eid for eid,port in m['ports'].items()if port.get('shared_landing_index')==i}
                shared_b={eid for eid,port in other['ports'].items()if port.get('shared_landing_index')==j}
                if shared_a&shared_b and all(abs(x-y)<.01 for x,y in zip(a,b)):
                    shared_ours.add(i);shared_theirs.add(j);continue
                if len(examples)<12:examples.append(dict(reason='actual_shape_overlap',node=m['id'],peer=other['id'],rect=a,peer_rect=b,position=p,peer_position=q))
                return 'actual_shape_overlap'
        # An explicitly identical shared landing is already the Module's own
        # collider. It is deduplicated by the assembler; do not classify that
        # same collider a second time as a foreign obstruction.
        foreign_theirs=[r for i,r in enumerate(theirs)if i not in shared_theirs]
        foreign_ours=[r for i,r in enumerate(rects)if i not in shared_ours]
        if any(intersects(translated(a,p),b)for a in md for b in foreign_theirs)or any(intersects(a,translated(b,q))for a in foreign_ours for b in od):return 'dynamic_sweep_into_neighbor'
        if mode=='shape_action':
            solid_theirs=[r for i,r in enumerate(theirs)if i not in other['case']['one_way_platform_indices']]
            solid_ours=[r for i,r in enumerate(rects)if i not in m['case']['one_way_platform_indices']]
            if any(intersects(translated(a,p),b)for a in mc for b in solid_theirs)or any(intersects(a,translated(b,q))for a in solid_ours for b in oc):return 'actual_action_space_blocked'
        return None
    def geometry(m,p):
        for key,other in selected.items():
            q=positions[key]
            # Conservative whole-union broad phase. No actual constraint is
            # removed: every narrow-phase collision lies within both bounds.
            if mode!='aabb'and not intersects(translated(local(m)[3],p),translated(local(other)[3],q)):continue
            ck=(id(m),id(other),p[0]-q[0],p[1]-q[1])
            if ck not in pair_cache:pair_cache[ck]=pair_reason(m,p,other,q)
            reason=pair_cache[ck]
            if reason:reject(reason);return False
        return True
    def recurse():
        nonlocal expanded
        if len(selected)==len(candidates):return True
        if expanded>=budget:return False
        if not remaining_chains_possible():reject('remaining_port_displacement_unsatisfied');return False
        remaining=[k for k in candidates if k not in selected]
        def closure_distance(k):
            origins={peer for _,peer in adjacent[k]if peer in selected};front=[(k,0)];visited={k}
            while front:
                n,d=front.pop(0)
                for _,peer in adjacent[n]:
                    if peer in selected:
                        if peer not in origins:return d+1
                        continue
                    if peer not in visited:visited.add(peer);front.append((peer,d+1))
            return 100000
        key=min(remaining,key=lambda k:(-sum(peer in selected for _,peer in adjacent[k]),closure_distance(k),-len(adjacent[k]),len(candidates[k]),k))
        for m in candidates[key]:
            if expanded>=budget:return False
            expanded+=1
            if expanded>budget:return False
            pose=None;valid=True
            for e,peer in adjacent[key]:
                if peer not in selected:continue
                other=selected[peer];a=m['ports'][e['id']];b=other['ports'][e['id']]
                if a['normal']!=[-x for x in b['normal']]:reject('port_normal');valid=False;break
                if not compatible_state(m,other,abilities):reject('motion_or_capability_condition');valid=False;break
                expected=[positions[peer][i]+b['position'][i]-a['position'][i]for i in range(2)]
                if a.get('aperture')and b.get('aperture'):
                    u=translated(a['aperture'],expected);v=translated(b['aperture'],positions[peer])
                    if min(u[0]+u[2],v[0]+v[2])-max(u[0],v[0])<24 or min(u[1]+u[3],v[1]+v[3])-max(u[1],v[1])<36:
                        reject('actor_aperture_too_small');valid=False;break
                if pose is not None and any(abs(x-y)>.01 for x,y in zip(pose,expected)):reject('cycle_closure');valid=False;break
                pose=expected
            if not valid:continue
            if pose is None:
                if selected:reject('disconnected_frontier');continue
                pose=[0,0]
            if not geometry(m,pose):continue
            selected[key]=m;positions[key]=pose
            if len(trace)<200:trace.append(dict(event='place',node=key,variant=m['variant_id'],position=pose))
            if recurse():return True
            selected.pop(key);positions.pop(key)
            if len(trace)<200:trace.append(dict(event='backtrack',node=key))
        return False
    ok=recurse();result=dict(schema='pcg/shape-search-layout/v1',seed=seed,mode=mode,status='feasible'if ok else'budget_exhausted'if expanded>=budget else'unsatisfied',
        expanded=expanded,budget=budget,wall_seconds=time.perf_counter()-started,rejections=rejects,trace=trace,
        rejection_examples=examples,placements={k:dict(position=positions[k],variant=selected[k]['variant_id'],shape_sha256=selected[k]['source_shape_sha256'])for k in selected}if ok else{},
        consumes=['actual canonical-derived collider rectangles and closed gates','saw sweep envelopes','actual local ports and apertures','capability/motion requirements','measured body action samples'],
        topology_sha256=digest(graph),source_placement_hints=False)
    if ok:
        modules=[]
        for n in graph['nodes']:
            m=copy.deepcopy(selected[n['id']]);m['spec']['placement']=positions[n['id']];modules.append(m)
        result['modules']=modules
        result['layout_signature']=digest({k:dict(position=[round(x,3)for x in positions[k]],variant=selected[k]['variant_id'])for k in sorted(selected)})
    return result
