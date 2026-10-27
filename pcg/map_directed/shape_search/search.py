"""Bounded CSP: actual port poses, collider unions and measured action space."""
import copy,random,time,math
from .catalog import rect_bounds
from pcg.prototype.factory.core.quality import digest

def translated(r,p):return [r[0]+p[0],r[1]+p[1],r[2],r[3]]
def intersects(a,b):return min(a[0]+a[2],b[0]+b[2])-max(a[0],b[0])>.25 and min(a[1]+a[3],b[1]+b[3])-max(a[1],b[1])>.25
def closed_solids(m):
    # Original ShotLatch.bind_motion_control disables its dummy gate collider.
    return m['case']['platforms']+[g['bounds']for g in m.get('boundary_gates',[])]+[l['gate'] for l in m['case'].get('latches',[])if not l.get('ferry_id')]
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

def geometry_conflict(m,p,other,q,mode='shape_action',allow_shared_air=False):
    ours,md,mc=closed_solids(m),sweeps(m),m['action_clearance'];theirs0,od,oc=closed_solids(other),sweeps(other),other['action_clearance']
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

def search(graph,domains,seed,mode='shape_action',budget=50000,abilities=None,entry_state=None,require_blocks=False,allow_shared_air=False,solution_check=None,ideal_scale_blocks=None,forward_check=False,probe_budget=None,wall_budget_seconds=None):
    started=time.perf_counter();rng=random.Random(seed);abilities=abilities or ['move','jump','shot_recoil']
    def timed_out():return wall_budget_seconds is not None and time.perf_counter()-started>=wall_budget_seconds
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
    cycle_audit=[]
    if require_blocks:
        from .cycles import prune
        candidates,cycle_audit=prune(graph,candidates)
        if any(not values for values in candidates.values()):return dict(status='unsatisfied',reason='cycle_port_contract_inconsistent',expanded=0,budget=budget,wall_seconds=time.perf_counter()-started,maximum_placed=0,best_partial={},cycle_domain_pruning=cycle_audit,rejections={'cycle_port_contract_inconsistent':1},trace=[],modules=[])
    for values in candidates.values():rng.shuffle(values)
    selected={};positions={};grid_positions={};expanded=0;probes=0;probe_limit=probe_budget if probe_budget is not None else budget*32;rejects={};trace=[];examples=[]
    def reject(reason):rejects[reason]=rejects.get(reason,0)+1
    displacement_cache={};chain_displacements={};oriented_cache={};best_partial={}
    def port_mode(p):return tuple(p['normal'])+(p.get('grid',{}).get('profile','legacy'),)+tuple(p.get('crossing_offset',[0,0]))
    def chain_deltas(part_keys,start_port,end_port):
        signature=(tuple(part_keys),port_mode(start_port),port_mode(end_port))
        if signature in chain_displacements:return chain_displacements[signature]
        if len(chain_displacements)>=4096:chain_displacements.clear()
        initial=port_mode(start_port);states={(0,0,*initial)}
        for ck in part_keys:
            if ck not in oriented_cache:
                key,a,b=ck;oriented_cache[ck]={(port_mode(m['ports'][a]),port_mode(m['ports'][b]),m['ports'][b]['position'][0]-m['ports'][a]['position'][0],m['ports'][b]['position'][1]-m['ports'][a]['position'][1])for m in candidates[key]}
            following=set()
            for dx,dy,nx,ny,profile,ox,oy in states:
                for incoming,outgoing,sx,sy in oriented_cache[ck]:
                    if incoming[:2]!=(-nx,-ny)or incoming[2:]!=(profile,ox,oy):continue
                    following.add((dx+sx,dy+sy,*outgoing))
            states=following
            if len(states)>10000:chain_displacements[signature]=None;return None
            if not states:break
        mode=port_mode(end_port);answer={(x,y)for x,y,nx,ny,profile,ox,oy in states if (nx,ny)==(-mode[0],-mode[1])and(profile,ox,oy)==mode[2:]}
        chain_displacements[signature]=answer;return answer
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
                        possible=chain_deltas(part_keys,selected[anchor]['ports'][first['id']],selected[key]['ports'][incoming['id']])
                        if possible is not None and tuple(desired)not in possible:return False

        return True
    path_topology_cache={}
    def pending_paths_possible():
        # A multi-Port junction also has finite shape. Checking only degree2
        # chains misses paths through two unplaced junctions, allowing the
        # surrounding map to demand an impossible2304px rise from a1792px pair.
        signature=tuple(sorted(selected))
        if signature not in path_topology_cache:
            checks=[]
            for anchor in selected:
                for first,neighbor in adjacent[anchor]:
                    if neighbor in selected:continue
                    queue=[(neighbor,first,[],frozenset([anchor]))];seen=set()
                    while queue:
                        key,incoming,parts,visited=queue.pop(0)
                        if key in selected:
                            if parts:checks.append((anchor,first['id'],key,incoming['id'],tuple(parts)))
                            continue
                        if key in seen or len(parts)>=6:continue
                        seen.add(key)
                        for outgoing,peer in adjacent[key]:
                            if outgoing['id']==incoming['id']:continue
                            if peer in visited and peer not in selected:continue
                            queue.append((peer,outgoing,parts+[(key,incoming['id'],outgoing['id'])],visited|{key}))
            if len(path_topology_cache)<4096:path_topology_cache[signature]=checks
        else:checks=path_topology_cache[signature]
        for anchor,first,dest,last,parts in checks:
            ap=selected[anchor]['ports'][first];bp=selected[dest]['ports'][last]
            desired=tuple(positions[dest][i]+bp['position'][i]-positions[anchor][i]-ap['position'][i]for i in range(2))
            bounds=[]
            for ck in parts:
                if ck not in displacement_cache:
                    key,a,b=ck;values=[[m['ports'][b]['position'][i]-m['ports'][a]['position'][i]for i in range(2)]for m in candidates[key]]
                    displacement_cache[ck]=([min(v[i]for v in values)for i in range(2)],[max(v[i]for v in values)for i in range(2)],set(map(tuple,values)))
                bounds.append(displacement_cache[ck])
            within=all(sum(p[0][i]for p in bounds)<=desired[i]<=sum(p[1][i]for p in bounds)for i in range(2))
            possible=chain_deltas(parts,ap,bp)if within else set()
            if possible is not None and desired not in possible:
                reject('unplaced_path_port_displacement_unsatisfied')
                if len(examples)<12:examples.append(dict(reason='unplaced_path_port_displacement_unsatisfied',anchor=anchor,destination=dest,path=list(parts),required_delta=desired))
                return False
        return True
    local_cache={};pair_cache={};hard_cell_cache={}
    def hard_cells(m,p):
        from ..block_grid.contracts import regions,raster
        key=(id(m['case']),id(m.get('boundary_gates')))
        if key not in hard_cell_cache:
            g=m['block_grid'];step=math.gcd(g['size'],32);hard_cell_cache[key]=set().union(*(raster(r,step,g['origin'])for r in regions(dict(m,action_clearance=[]))))
        g=m['block_grid'];step=math.gcd(g['size'],32);dx,dy=[round((p[i]+g['origin'][i])/step)for i in range(2)]
        return {(x+dx,y+dy)for x,y in hard_cell_cache[key]}
    def local(m):
        k=(id(m['case']),id(m['action_clearance']),id(m.get('boundary_gates')))
        if k not in local_cache:
            rects=closed_solids(m);dynamic=sweeps(m);clearance=m['action_clearance']
            extra=[]
            if allow_shared_air:
                from ..block_grid.contracts import regions
                extra=regions(dict(m,action_clearance=[]))
            a=rect_bounds(rects+dynamic+clearance+extra)
            local_cache[k]=(rects,dynamic,clearance,[a[0],a[1],a[2]-a[0],a[3]-a[1]])
        return local_cache[k]
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
            def identity(v):return (id(v['case']),id(v['action_clearance']),id(v.get('boundary_gates')),tuple((eid,port.get('shared_landing_index'))for eid,port in v['ports'].items()if 'shared_landing_index'in port))
            ck=(identity(m),identity(other),p[0]-q[0],p[1]-q[1])
            if ck not in pair_cache:
                if len(pair_cache)>=50000:pair_cache.clear()
                pair_cache[ck]=geometry_conflict(m,p,other,q,mode,allow_shared_air)
            reason=pair_cache[ck]
            if reason:reject(reason);return False
        return True
    def candidate_pose(key,m):
        nonlocal probes
        if probes>=probe_limit or timed_out():return None
        probes+=1
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
        if not valid:return None
        if pose is None:
            if selected:reject('disconnected_frontier');return None
            pose=[0,0]
            if require_blocks:grid_pose=[0,0]
        if not geometry(m,pose):return None
        return pose,grid_pose
    def recurse():
        nonlocal expanded,best_partial
        if len(selected)>len(best_partial):best_partial={k:dict(variant=selected[k]['variant_id'],position=positions[k][:])for k in selected}
        if len(selected)==len(candidates):
            if solution_check is not None:
                proposed=[]
                for n in graph['nodes']:
                    m=copy.deepcopy(selected[n['id']]);m['spec']['placement']=positions[n['id']]
                    if require_blocks:m['spec']['block_placement']=grid_positions[n['id']]
                    proposed.append(m)
                if not solution_check(proposed):reject('solution_contract_rejected');return False
            return True
        if expanded>=budget or probes>=probe_limit or timed_out():return False
        if not remaining_chains_possible():reject('remaining_port_displacement_unsatisfied');return False
        if forward_check and require_blocks and not pending_paths_possible():return False
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
        live_poses={};frontier={}
        if forward_check and selected:
            for k in remaining:
                if not any(peer in selected for _,peer in adjacent[k]):continue
                options=[]
                for m in candidates[k]:
                    if probes>=probe_limit or timed_out():return False
                    placement=candidate_pose(k,m)
                    if placement is not None:options.append(m);live_poses[id(m)]=placement
                if not options:reject('frontier_domain_wipeout');return False
                frontier[k]=options
            if not frontier:reject('disconnected_frontier');return False
            key=min(frontier,key=lambda k:(len(frontier[k]),-sum(peer in selected for _,peer in adjacent[k]),closure_distance(k),-len(adjacent[k]),k));ordered=frontier[key]
        else:
            key=min(remaining,key=lambda k:(-sum(peer in selected for _,peer in adjacent[k]),closure_distance(k),-len(adjacent[k]),len(candidates[k]),k));ordered=candidates[key]
        if ideal_scale_blocks is not None:
            node_by={n['id']:n for n in graph['nodes']}
            def preference(m):
                target=node_by[key].get('ideal',[0,0]);cost=0.
                if selected:
                    root=next(iter(selected));ref=node_by[root].get('ideal',[0,0]);anchor=selected[root];center=[sum(p['position'][i]for p in anchor['ports'].values())/len(anchor['ports'])+positions[root][i]for i in range(2)]
                    for e,peer in adjacent[key]:
                        if peer not in selected:continue
                        a=m['ports'][e['id']];b=selected[peer]['ports'][e['id']]
                        if a['normal']!=[-v for v in b['normal']]:return 1e20
                        origin=[positions[peer][i]+b['position'][i]-a['position'][i]for i in range(2)]
                        at=[sum(p['position'][i]for p in m['ports'].values())/len(m['ports'])+origin[i]for i in range(2)]
                        return sum((at[i]-center[i]-(target[i]-ref[i])*ideal_scale_blocks*128)**2 for i in range(2))
                for e,peer in adjacent[key]:
                    other=node_by[peer].get('ideal',[0,0]);p=m['ports'][e['id']]
                    cost-=sum(p['normal'][i]*(other[i]-target[i])for i in range(2))*1000
                return cost
            ordered=sorted(ordered,key=preference)
        for m in ordered:
            if expanded>=budget or probes>=probe_limit or timed_out():return False
            expanded+=1
            if expanded>budget:return False
            placement=live_poses.get(id(m))if forward_check and selected else candidate_pose(key,m)
            if placement is None:continue
            pose,grid_pose=placement
            selected[key]=m;positions[key]=pose
            if require_blocks:grid_positions[key]=grid_pose
            if len(trace)<200:trace.append(dict(event='place',node=key,variant=m['variant_id'],position=pose))
            if recurse():return True
            selected.pop(key);positions.pop(key);grid_positions.pop(key,None)
            if len(trace)<200:trace.append(dict(event='backtrack',node=key))
        return False
    ok=recurse();result=dict(schema='pcg/shape-search-layout/v1',seed=seed,mode=mode,status='feasible'if ok else'budget_exhausted'if expanded>=budget or probes>=probe_limit or timed_out() else'unsatisfied',
        expanded=expanded,budget=budget,feasibility_probes=probes,probe_budget=probe_limit,forward_check=forward_check,cycle_domain_pruning=cycle_audit,wall_seconds=time.perf_counter()-started,rejections=rejects,trace=trace,
        rejection_examples=examples,placements={k:dict(position=positions[k],variant=selected[k]['variant_id'],shape_sha256=selected[k]['source_shape_sha256'])for k in selected}if ok else{},
        maximum_placed=len(best_partial),best_partial=best_partial,wall_budget_seconds=wall_budget_seconds,wall_budget_exhausted=timed_out(),consumes=['actual canonical-derived collider rectangles and closed gates','saw sweep envelopes','actual local ports and apertures','capability/motion requirements','measured body action samples'],
        topology_sha256=digest(graph),source_placement_hints=False,abstract_graph_ideal_ordering=ideal_scale_blocks,block_grid_required=require_blocks,shared_air_only=allow_shared_air,block_origins=grid_positions.copy()if ok and require_blocks else{},coordinate_system='integer Block origins; pixels only for narrow-phase geometry'if require_blocks else'legacy pixel origins')
    if ok:
        modules=[]
        for n in graph['nodes']:
            m=copy.deepcopy(selected[n['id']]);m['spec']['placement']=positions[n['id']]
            if require_blocks:m['spec']['block_placement']=grid_positions[n['id']]
            modules.append(m)
        result['modules']=modules
        result['layout_signature']=digest({k:dict(position=[round(x,3)for x in positions[k]],variant=selected[k]['variant_id'])for k in sorted(selected)})
    return result
