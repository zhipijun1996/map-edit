"""CP-SAT backend for the existing exact Block/shape search contract.

Tables couple candidate choice, all Port poses and integer origins. Optional
union rectangles enforce solid occupancy; the original narrow phase rejects
foreign action/dynamic conflicts. No geometry or topology is produced here.
"""
import copy,hashlib,itertools,time
from ortools.sat.python import cp_model
from .search import search,geometry_conflict,compatible_state,intersects,translated
from ..block_grid.contracts import validate,regions,raster
from pcg.prototype.factory.core.quality import digest


def union_rectangles(cells):
    rows={}
    for x,y in cells:rows.setdefault(y,[]).append(x)
    active={};rects=[]
    for y in sorted(rows):
        spans=[]
        for x in sorted(rows[y]):
            if spans and spans[-1][1]==x:spans[-1][1]+=1
            else:spans.append([x,x+1])
        following={}
        for a,b in spans:
            r=active.get((a,b))
            if r is not None and r[1]+r[3]==y:r[3]+=1
            else:r=[a,y,b-a,1];rects.append(r)
            following[(a,b)]=r
        active=following
    return rects


def solve(graph,domains,seed,seconds=40,rounds=64,abilities=None,occupancy=True,layout_preference=False):
    started=time.perf_counter();abilities=abilities or ['move','jump','shot_recoil'];clean={};excluded=[]
    for k,values in domains.items():
        clean[k]=[]
        for m in values:
            errors=validate(m)
            if errors or not compatible_state(m,m,abilities):excluded.append(dict(node=k,variant=m['variant_id'],errors=errors or ['motion_contract']))
            else:clean[k].append(m)
    if any(not vs for vs in clean.values()):return dict(status='unsatisfied',reason='empty_qualified_domain',empty_domains=[k for k,vs in clean.items()if not vs],excluded=excluded,modules=[])
    size={m['block_grid']['size']for vs in clean.values()for m in vs}
    if size!={128}:raise ValueError('CP_backend_currently_requires_Block128')
    model=cp_model.CpModel();variables={};geometry={};ix=[];iy=[];signatures={};tables=0
    radius=int(sum(max(max(abs(v)for p in m['ports'].values()for v in p['position'])for m in vs)//128+2 for vs in clean.values()))
    for key,vs in clean.items():
        x=model.new_int_var(-radius,radius,key+'/bx');y=model.new_int_var(-radius,radius,key+'/by');choice=model.new_int_var(0,len(vs)-1,key+'/candidate');groups={};by=[];unique=[]
        for m in vs:
            sig=(id(m['case']),id(m['action_clearance']))
            if sig not in groups:groups[sig]=len(unique);unique.append(m)
            by.append(groups[sig])
        shape=model.new_int_var(0,len(unique)-1,key+'/shape');model.add_allowed_assignments([choice,shape],list(enumerate(by)))
        variables[key]=dict(x=x,y=y,v=choice,g=shape);geometry[key]=(by,unique)
        for i,m in enumerate(unique):
            present=model.new_bool_var(key+'/shape'+str(i));model.add(shape==i).only_enforce_if(present);model.add(shape!=i).only_enforce_if(present.Not())
            cells=set().union(*(raster(r,32)for r in regions(dict(m,action_clearance=[]))))
            for j,(a,b,w,h)in enumerate(union_rectangles(cells)):
                ix.append(model.new_optional_fixed_size_interval_var(4*x+a,w,present,key+'/x'+str(i)+'/'+str(j)))
                iy.append(model.new_optional_fixed_size_interval_var(4*y+b,h,present,key+'/y'+str(i)+'/'+str(j)))
    root=max(clean,key=lambda k:sum(k in[e['from'],e['to']]for e in graph['edges']));model.add(variables[root]['x']==0);model.add(variables[root]['y']==0)
    profiles={p['grid']['profile']+repr(p.get('crossing_offset',[0,0]))for vs in clean.values()for m in vs for p in m['ports'].values()};profiles={k:i for i,k in enumerate(sorted(profiles))}
    for edge in graph['edges']:
        ends=[]
        for key in [edge['from'],edge['to']]:
            vs=clean[key];xs=[];ys=[];data=[]
            for i,m in enumerate(vs):
                p=m['ports'][edge['id']];px,py=[round(v/64)for v in p['position']]
                if any(abs(v/64-round(v/64))>1e-6 for v in p['position']):raise ValueError('non_Block_Port')
                row=[i,px,py,*p['normal'],profiles[p['grid']['profile']+repr(p.get('crossing_offset',[0,0]))]];data.append(row);xs.append(px);ys.append(py)
            q=[model.new_int_var(min(xs),max(xs),key+'/'+edge['id']+'/px'),model.new_int_var(min(ys),max(ys),key+'/'+edge['id']+'/py'),model.new_int_var(-1,1,key+'/'+edge['id']+'/nx'),model.new_int_var(-1,1,key+'/'+edge['id']+'/ny'),model.new_int_var(0,len(profiles)-1,key+'/'+edge['id']+'/profile')]
            model.add_allowed_assignments([variables[key]['v']]+q,data);tables+=1;ends.append((variables[key],q))
        (a,p),(b,q)=ends
        model.add(2*a['x']+p[0]==2*b['x']+q[0]);model.add(2*a['y']+p[1]==2*b['y']+q[1]);model.add(p[2]==-q[2]);model.add(p[3]==-q[3]);model.add(p[4]==q[4])
    if occupancy:model.add_no_overlap_2d(ix,iy)
    if layout_preference:
        ideals={n['id']:n.get('ideal',[0,0])for n in graph['nodes']};reference=ideals[root];deviations=[]
        for key,v in variables.items():
            for axis,field in enumerate(['x','y']):
                desired=round((ideals[key][axis]-reference[axis])*.4)
                delta=model.new_int_var(0,2*radius,'ideal-distance/'+key+'/'+field);model.add_abs_equality(delta,v[field]-desired);deviations.append(delta);model.add_hint(v[field],desired)
        model.minimize(sum(deviations))
    history=[];attempted=[];hard_cache={};air_cache={}
    def physical_rectangles(m):
        k=id(m['case'])
        if k not in hard_cache:
            cells=set().union(*(raster(r,32)for r in regions(dict(m,action_clearance=[]))))
            hard_cache[k]=[[a*32,b*32,w*32,h*32]for a,b,w,h in union_rectangles(cells)]
        return hard_cache[k]
    def witness(a,p,b,q):
        pairs=[(physical_rectangles(a),physical_rectangles(b),'block_occupancy_overlap'),(a['action_clearance'],regions(dict(b,action_clearance=[])),'foreign_occupancy_blocks_action'),(regions(dict(a,action_clearance=[])),b['action_clearance'],'foreign_occupancy_blocks_action')]
        for aa,bb,reason in pairs:
            for ra in aa:
                for rb in bb:
                    if intersects(translated(ra,p),translated(rb,q)):return ra,rb,reason
        return None
    for round_index in range(rounds):
        left=seconds-(time.perf_counter()-started)
        if left<=0:break
        solver=cp_model.CpSolver();solver.parameters.max_time_in_seconds=left;solver.parameters.num_search_workers=1;solver.parameters.stop_after_first_solution=True;solver.parameters.random_seed=int(hashlib.sha256(seed.encode()).hexdigest()[:7],16)
        status=solver.solve(model);entry=dict(round=round_index,status=solver.status_name(status),seconds=solver.wall_time,branches=solver.num_branches,conflicts=solver.num_conflicts);history.append(entry)
        if status not in [cp_model.FEASIBLE,cp_model.OPTIMAL]:break
        selected={k:clean[k][solver.value(v['v'])]for k,v in variables.items()};poses={k:[128*solver.value(v['x']),128*solver.value(v['y'])]for k,v in variables.items()};conflicts=[]
        for a,b in itertools.combinations(selected,2):
            hit=witness(selected[a],poses[a],selected[b],poses[b]);reason=geometry_conflict(selected[a],poses[a],selected[b],poses[b],allow_shared_air=True)
            if hit or reason:conflicts.append((a,b,reason or hit[2],hit))
        entry['narrow_phase_conflicts']=[dict(a=a,b=b,reason=r)for a,b,r,_ in conflicts]
        if not conflicts:
            # Reuse original exact Block/state/shape verifier and placement path.
            check=search(graph,{k:[m]for k,m in selected.items()},seed+'/exact-check',budget=len(selected)+1,require_blocks=True,allow_shared_air=True,abilities=abilities)
            if check['status']!='feasible':return dict(status='exact_check_rejected',history=history,check=check,modules=[])
            check.update(backend='CP-SAT candidate/Port/Block tables + original exact narrow phase',cp_history=history,cp_optional_rectangles=len(ix),cp_port_tables=tables,total_wall_seconds=time.perf_counter()-started,abstract_layout_soft_preference=layout_preference,topology_sha256=digest(graph));return check
        model.clear_hints()
        for key,v in variables.items():
            for item in ['x','y','v','g']:model.add_hint(v[item],solver.value(v[item]))
        for a,b,reason,hit in conflicts:
            av,bv=variables[a],variables[b];ga=solver.value(av['g']);gb=solver.value(bv['g']);literals=[]
            for expression,value in [(av['g'],ga),(bv['g'],gb)]:
                same=model.new_bool_var('lazy/'+str(len(attempted))+'/'+str(len(literals)));model.add(expression==value).only_enforce_if(same);model.add(expression!=value).only_enforce_if(same.Not());literals.append(same.Not())
            if hit:
                import math
                ra,rb,_=hit
                for axis in [0,1]:
                    low=math.ceil((rb[axis]-ra[axis]-ra[axis+2]+.251)/128);high=math.floor((rb[axis]+rb[axis+2]-ra[axis]-.251)/128);delta=av['x'if axis==0 else'y']-bv['x'if axis==0 else'y']
                    below=model.new_bool_var('below/'+str(len(attempted))+'/'+str(axis));above=model.new_bool_var('above/'+str(len(attempted))+'/'+str(axis));model.add(delta<low).only_enforce_if(below);model.add(delta>high).only_enforce_if(above);literals.extend([below,above])
            else:
                for axis in [0,1]:
                    field='x'if axis==0 else'y';delta=av[field]-bv[field];current=(poses[a][axis]-poses[b][axis])//128
                    diff=model.new_bool_var('different/'+str(len(attempted))+'/'+field);model.add(delta!=current).only_enforce_if(diff);literals.append(diff)
            model.add_bool_or(literals);attempted.append(dict(a=a,b=b,shape_a=ga,shape_b=gb,witness=hit,reason=reason))
    return dict(status='unsatisfied'if history and history[-1]['status']=='INFEASIBLE'else'budget_exhausted',backend='CP-SAT',budget_seconds=seconds,wall_seconds=time.perf_counter()-started,history=history,lazy_conflicts=attempted,modules=[],topology_sha256=digest(graph))
