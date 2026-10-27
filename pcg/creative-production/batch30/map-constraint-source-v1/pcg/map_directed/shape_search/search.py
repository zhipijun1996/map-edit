"""Bounded CSP: actual port poses, collider unions and measured action space."""
import copy,random,time,math
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

def search(graph,domains,seed,mode='shape_action',budget=50000,abilities=None,entry_state=None,require_blocks=False,allow_shared_air=False):
    started=time.perf_counter();rng=random.Random(seed);abilities=abilities or ['move','jump','shot_recoil']
    adjacent={n['id']:[]for n in graph['nodes']}
    for e in graph['edges']:
        adjacent[e['from']].append((e,e['to']));adjacent[e['to']].append((e,e['from']))
    candidates={k:[m for m in v if compatible_state(m,m,abilities,entry_state)]for k,v in domains.items()}
    if require_blocks:
        from ..block_grid.contracts import validate as validate_blocks,placed_cells,same_profile,joined_block_origin
        rejected=[]
        for key,values in candidates.items():
            clean=[]
            for m in values:
                errors=validate_blocks(m)
                if errors:rejected.append(dict(node=key,variant=m['variant_id'],errors=errors))
                else:clean.append(m)
            candidates[key]=clean
        sizes={m['block_grid']['size']for vs in candidates.values()for m in vs}
        if len(sizes)>1:raise ValueError('mixed_block_sizes_in_one_map')
        if any(not vs for vs in candidates.values()):
            return dict(status='unsatisfied',reason='no_block_compatible_candidate',expanded=0,budget=budget,rejected=rejected,modules=[])
    for values in candidates.values():rng.shuffle(values)
    selected={};positions={};grid_positions={};expanded=0;rejects={};trace=[];examples=[]
    def reject(reason):rejects[reason]=rejects.get(reason,0)+1
    displacement_cache={};chain_displacements={}
    def remaining_chains_possible():
        # A chain between two placed anchors has a known remaining port delta.
        # Reject impossible intervals before enumerating every geometric pose.
        for anchor in selected:
            for first,neighbor in adjacent[anchor]:
                if neighbor in selected:continue
                key=neighbor;incoming=first;parts=[];part_keys=[];seen=set()
                while key not in selected and len(adjacent[key])==2 and key not in seen:
                    seen.add(key);outgoing,peer=next((e,p)for e,p in adjacent[key]if e['id']!=incoming['id'])
                    ck=(key,incoming['id'],outgoing['id'])
                    if ck not in displacement_cache:
                        values=[[m['ports'][outgoing['id']]['position'][i]-m['ports'][incoming['id']]['position'][i]for i in range(2)]for m in candidates[key]]
                        if not values:return False
                        displacement_cache[ck]=([min(v[i]for v in values)for i in range(2)],[max(v[i]for v in values)for i in range(2)],set(map(tuple,values)))
                    parts.append(displacement_cache[ck]);part_keys.append(ck);key=peer;incoming=outgoing
                if key in selected and parts:
                    a=selected[anchor]['ports'][first['id']]['position'];b=selected[key]['ports'][incoming['id']]['position']
                    desired=[positions[key][i]+b[i]-positions[anchor][i]-a[i]for i in range(2)]
                    if any(desired[i]<sum(p[0][i]for p in parts)-.01 or desired[i]>sum(p[1][i]for p in parts)+.01 for i in range(2)):return False
                    if require_blocks:
                        signature=tuple(part_keys)
                        if signature not in chain_displacements:
                            possible={(0,0)}
                            for part in parts:
                                possible={(a+c,b+d)for a,b in possible for c,d in part[2]}
                                if len(possible)>4096:possible=None;break
                            chain_displacements[signature]=possible
                        possible=chain_displacements[signature]
                        if possible is not None and tuple(desired)not in possible:return False
        return True
    local_cache={};pair_cache={};hard_cell_cache={}
    def hard_cells(m,p):
        from ..block_grid.contracts import regions,raster
        key=id(m)
        if key not in hard_cell_cache:
            g=m['block_grid'];step=math.gcd(g['size'],32);hard_cell_cache[key]=set().union(*(raster(r,step,g['origin'])for r in regions(dict(m,action_clearance=[]))))
        g=m['block_grid'];step=math.gcd(g['size'],32);dx,dy=[round((p[i]+g['origin'][i])/step)for i in range(2)]
        return {(x+dx,y+dy)for x,y in hard_cell_cache[key]}
    def local(m):
        k=id(m)
        if k not in local_cache:
            rects=closed_solids(m);dynamic=sweeps(m);clearance=m['action_clearance']
            extra=[]
            if allow_shared_air:
                from ..block_grid.contracts import regions
                extra=regions(dict(m,action_clearance=[]))
            a=rect_bounds(rects+dynamic+clearance+extra)
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
            if allow_shared_air:
                from ..block_grid.contracts import regions
                # A shared coarse Block is only a broad-phase candidate. Body
                # samples must still avoid ALL foreign solids, hazards and
                # full dynamic envelopes, including foreign one-way supports.
                foreign_a=regions(dict(m,action_clearance=[]));foreign_b=regions(dict(other,action_clearance=[]))
                if any(intersects(translated(a,p),translated(b,q))for a in mc for b in foreign_b)or any(intersects(translated(a,p),translated(b,q))for a in foreign_a for b in oc):return 'foreign_occupancy_blocks_action'
            solid_theirs=[r for i,r in enumerate(theirs)if i not in other['case']['one_way_platform_indices']]
            solid_ours=[r for i,r in enumerate(rects)if i not in m['case']['one_way_platform_indices']]
            if any(intersects(translated(a,p),b)for a in mc for b in solid_theirs)or any(intersects(a,translated(b,q))for a in solid_ours for b in oc):return 'actual_action_space_blocked'
        return None
    def geometry(m,p):
        if require_blocks:
            try:ours=placed_cells(m,p)
            except ValueError:reject('placement_not_block_aligned');return False
            for key,other in selected.items():
                shared=ours&placed_cells(other,positions[key])
                if shared:
                    material=hard_cells(m,p)&hard_cells(other,positions[key])if allow_shared_air else shared
                    if allow_shared_air and not material:continue
                    if len(examples)<12:examples.append(dict(reason='block_occupancy_overlap',node=m['id'],peer=other['id'],variant=m['variant_id'],peer_variant=other['variant_id'],shared_cells=sorted(map(list,shared)),material_cells=sorted(map(list,material)),position=p,peer_position=positions[key]))
                    reject('block_occupancy_overlap');return False
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
            pose=None;grid_pose=None;valid=True
            for e,peer in adjacent[key]:
                if peer not in selected:continue
                other=selected[peer];a=m['ports'][e['id']];b=other['ports'][e['id']]
                if a['normal']!=[-x for x in b['normal']]:reject('port_normal');valid=False;break
                if require_blocks and not same_profile(a,b):reject('seam_profile_mismatch');valid=False;break
                if not compatible_state(m,other,abilities):reject('motion_or_capability_condition');valid=False;break
                if require_blocks:
                    block_size=m['block_grid']['size'];candidate_grid=joined_block_origin(grid_positions[peer],b,a,other['block_grid']['origin'],m['block_grid']['origin'],block_size)
                    if grid_pose is not None and grid_pose!=candidate_grid:reject('grid_cycle_closure');valid=False;break
                    grid_pose=candidate_grid;expected=[v*block_size for v in candidate_grid]
                else:expected=[positions[peer][i]+b['position'][i]-a['position'][i]for i in range(2)]
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
                if require_blocks:grid_pose=[0,0]
            if not geometry(m,pose):continue
            selected[key]=m;positions[key]=pose
            if require_blocks:grid_positions[key]=grid_pose
            if len(trace)<200:trace.append(dict(event='place',node=key,variant=m['variant_id'],position=pose))
            if recurse():return True
            selected.pop(key);positions.pop(key);grid_positions.pop(key,None)
            if len(trace)<200:trace.append(dict(event='backtrack',node=key))
        return False
    ok=recurse();result=dict(schema='pcg/shape-search-layout/v1',seed=seed,mode=mode,status='feasible'if ok else'budget_exhausted'if expanded>=budget else'unsatisfied',
        expanded=expanded,budget=budget,wall_seconds=time.perf_counter()-started,rejections=rejects,trace=trace,
        rejection_examples=examples,placements={k:dict(position=positions[k],variant=selected[k]['variant_id'],shape_sha256=selected[k]['source_shape_sha256'])for k in selected}if ok else{},
        consumes=['actual canonical-derived collider rectangles and closed gates','saw sweep envelopes','actual local ports and apertures','capability/motion requirements','measured body action samples'],
        topology_sha256=digest(graph),source_placement_hints=False,block_grid_required=require_blocks,shared_air_only=allow_shared_air,block_origins=grid_positions.copy()if ok and require_blocks else{},coordinate_system='integer Block origins; pixels only for narrow-phase geometry'if require_blocks else'legacy pixel origins')
    if ok:
        modules=[]
        for n in graph['nodes']:
            m=copy.deepcopy(selected[n['id']]);m['spec']['placement']=positions[n['id']]
            if require_blocks:m['spec']['block_placement']=grid_positions[n['id']]
            modules.append(m)
        result['modules']=modules
        result['layout_signature']=digest({k:dict(position=[round(x,3)for x in positions[k]],variant=selected[k]['variant_id'])for k in sorted(selected)})
    return result
