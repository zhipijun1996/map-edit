"""Integer occupancy and port geometry. Never a replacement physics solver."""
import copy,math

EDGES={'W':(-1,0),'E':(1,0),'N':(0,-1),'S':(0,1)}
def anchor(cell,edge,size=128,origin=(0,0)):
    x,y=cell;dx,dy=EDGES[edge]
    return [origin[0]+(x+.5+dx*.5)*size,origin[1]+(y+.5+dy*.5)*size]

def raster(rect,size=128,origin=(0,0)):
    x,y,w,h=rect
    if not all(math.isfinite(v)for v in rect)or w<=0 or h<=0:raise ValueError('invalid_grid_region')
    a=math.floor((x-origin[0]+1e-6)/size);b=math.floor((x+w-origin[0]-1e-6)/size)
    c=math.floor((y-origin[1]+1e-6)/size);d=math.floor((y+h-origin[1]-1e-6)/size)
    return {(i,j)for i in range(a,b+1)for j in range(c,d+1)}

def regions(module):
    c=module['case'];out=list(c['platforms'])+list(c.get('hazards',[]))+list(module.get('action_clearance',[]))
    out += [g['bounds']for g in module.get('boundary_gates',[])]
    out += [b['action_bounds']for b in c.get('boss_encounters',[])]
    movers={p['platform_id']for p in c.get('moving_platforms',[])}
    out += [l['gate']for l in c.get('latches',[])if l.get('ferry_id')not in movers]
    out += [[l['bell'][0]-14,l['bell'][1]-17,28,34]for l in c.get('latches',[])]
    out += [[l['return_access'][0]-14,l['return_access'][1]-17,28,34]for l in c.get('latches',[])if l.get('return_access')]
    out += [[s['target']['position'][0]-21,s['target']['position'][1]-17,42,34]for s in c.get('reward_sites',[])if 'target'in s]
    for thorn in c.get('thorns',[]):
        x,y,w,h=c['platforms'][thorn['platform_index']];s=thorn['start_offset'];n=thorn['length'];z=thorn['depth']
        out.append({'top':[x+s,y-z,n,z],'bottom':[x+s,y+h,n,z],'left':[x-z,y+s,z,n],'right':[x+w,y+s,z,n]}[thorn['face']])
    for saw in c.get('saws',[]):
        x,y=saw['origin'];a,b=saw['travel'];r=saw['radius'];out.append([x-abs(a)-r,y-abs(b)-r,2*(abs(a)+r),2*(abs(b)+r)])
    for mover in c.get('moving_platforms',[]):
        a,b=mover['start'],mover['finish'];w,h=mover['size'];out.append([min(a[0],b[0])-w/2,min(a[1],b[1])-h/2,abs(a[0]-b[0])+w,abs(a[1]-b[1])+h])
    return out

def connected(cells):
    todo=set(map(tuple,cells))
    if not todo:return False
    front=[todo.pop()]
    while front:
        x,y=front.pop()
        for dx,dy in EDGES.values():
            q=(x+dx,y+dy)
            if q in todo:todo.remove(q);front.append(q)
    return not todo

def declare(module,cells,size=128):
    m=copy.deepcopy(module)
    m['block_grid']=dict(schema='map-notes/block-grid/v1',size=size,origin=[0,0],cells=sorted(map(list,set(map(tuple,cells)))),
        occupancy_coverage='declared entity + reserved action space',action_coverage='partial; concrete policies require actual Godot verification',
        roles=m.get('functional_roles',['traversal']),port_bindings=[dict(port_id=k,**p['grid'])for k,p in m['ports'].items()])
    return m

def validate(module):
    errors=[];g=module.get('block_grid')
    if not isinstance(g,dict)or g.get('schema')!='map-notes/block-grid/v1':return ['missing_block_grid_contract']
    size=g.get('size');origin=g.get('origin')
    if type(size)is not int or size<32 or size%2:return ['block_size_requires_even_integer_at_least_32']
    if not isinstance(origin,list)or len(origin)!=2 or any(type(x)is not int or x%size for x in origin):return ['grid_origin_not_block_aligned']
    raw=g.get('cells',[])
    if any(not isinstance(p,list)or len(p)!=2 or any(type(x)is not int for x in p)for p in raw):return ['invalid_block_cells']
    cells=set(map(tuple,raw))
    if len(cells)!=len(raw):errors.append('duplicate_block_cell')
    if not connected(cells):errors.append('disconnected_block_shape')
    for k,p in module['ports'].items():
        q=p.get('grid',{});cell=q.get('cell');edge=q.get('edge')
        if not isinstance(cell,list)or len(cell)!=2 or any(type(x)is not int for x in cell)or edge not in EDGES:errors.append('missing_grid_port/'+k);continue
        cell=tuple(cell)
        if cell not in cells:errors.append('port_cell_not_owned/'+k)
        dx,dy=EDGES[edge]
        if (cell[0]+dx,cell[1]+dy)in cells:errors.append('port_not_on_shape_boundary/'+k)
        if p['position']!=anchor(cell,edge,size,origin)or p['normal']!=[dx,dy]:errors.append('port_not_at_boundary_center/'+k)
        if not q.get('profile'):errors.append('missing_seam_profile/'+k)
    for r in regions(module):
        if not raster(r,size,origin)<=cells:errors.append('unreserved_physical_or_action_region');break
    if module['case'].get('enemies')and not module.get('enemy_envelopes_verified'):errors.append('enemy_full_envelope_unknown')
    return sorted(set(errors))

def placed_cells(module,position):
    g=module['block_grid'];b=g['size']
    if any(abs(v/b-round(v/b))>1e-7 for v in position):raise ValueError('placement_not_block_aligned')
    dx,dy=[round((position[i]+g['origin'][i])/b)for i in range(2)]
    return {(x+dx,y+dy)for x,y in g['cells']}

def same_profile(a,b):
    return a.get('grid',{}).get('profile')==b.get('grid',{}).get('profile')and a.get('crossing_offset',[0,0])==b.get('crossing_offset',[0,0])

def state_entails(ensures,requires):
    """Use existing contract field names. UNKNOWN never proves a requirement."""
    if ensures=='UNKNOWN'or requires=='UNKNOWN':return False
    for key,want in requires.items():
        have=ensures.get(key,'UNKNOWN')
        if want=='UNKNOWN'or have=='UNKNOWN':return False
        if isinstance(want,list)and len(want)==2 and all(type(v)in [int,float]for v in want):
            if not isinstance(have,list)or len(have)!=2 or not all(type(v)in [int,float]and math.isfinite(v)for v in have+want)or have[0]>have[1]or want[0]>want[1]or have[0]<want[0]or have[1]>want[1]:return False
        elif isinstance(want,dict):
            if not isinstance(have,dict)or not state_entails(have,want):return False
        elif have!=want:return False
    return True

def joined_block_origin(origin,a,b,a_grid_origin=(0,0),b_grid_origin=(0,0),size=128):
    """Exact integer grid join: B origin = A origin + A cell - B cell + nA."""
    if a['normal']!=[-v for v in b['normal']]:raise ValueError('opposed_grid_normals_required')
    if any(type(v)is not int for v in origin):raise ValueError('integer_block_origin_required')
    return [origin[i]+a['grid']['cell'][i]-b['grid']['cell'][i]+a['normal'][i]+a_grid_origin[i]//size-b_grid_origin[i]//size for i in range(2)]
