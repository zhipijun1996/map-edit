"""New bounded terminal-bank versions; content/geometry is never substituted."""
import copy,math,json
from ..catalog_feed.adapt import samples,target
from ..block_grid.contracts import declare,regions,raster,validate,connected
from pcg.prototype.plains.block_modules import port
from pcg.prototype.factory.core.quality import digest
from .catalog import describe,WORLD

def translate(case,dx,dy):
    c=copy.deepcopy(case)
    def pt(p):return[p[0]+dx,p[1]+dy]
    def rect(p):return[*pt(p),*p[2:]]
    c['platforms']=[rect(p)for p in c['platforms']];c['hazards']=[rect(p)for p in c.get('hazards',[])]
    for k in ['spawn','entry_port','exit_port']:c[k]=pt(c[k])
    c['goal']=rect(c['goal'])
    for p in c.get('ports',[]):p['position']=pt(p['position'])
    for p in c.get('latches',[]):
        p['bell']=pt(p['bell']);p['gate']=rect(p['gate'])
        if p.get('return_access'):p['return_access']=pt(p['return_access'])
    for p in c.get('moving_platforms',[]):p['start']=pt(p['start']);p['finish']=pt(p['finish'])
    for p in c.get('saws',[]):p['origin']=pt(p['origin'])
    for p in c.get('enemies',[]):p['position']=pt(p['position'])
    for p in c.get('hooks',[]):p['x']+=dx;p['y']+=dy
    for p in c.get('reward_sites',[]):
        p['position']=pt(p['position'])
        if p.get('region'):p['region']=rect(p['region'])
        p.pop('target',None)
    for p in c.get('shop_sites',[]):p['position']=pt(p['position'])
    for op in c['control_plan']:
        if 'target_x'in op:op['target_x']+=dx
        q=op.get('trigger',{}).get('dynamic',{})
        if q.get('kind')=='actor_x':q['value']+=dx
    return c

def adapt(item,phase=0,vertical_phase=0,normal_overrides=None,terminal_budget=32):
    d=describe(item);raw=item['cases'];base=raw[0]
    old_normals={k:p['normal'][:]for k,p in d['ports'].items()}
    for k,n in(normal_overrides or{}).items():d['ports'][k]['normal']=[n,0]
    if not d['shared_world']:raise ValueError('source_multi_route_world_mismatch')
    if any(c['capabilities']!=base['capabilities']for c in raw):raise ValueError('source_route_capability_profiles_differ')
    if any(c.get('enemies')for c in raw):raise ValueError('enemy_full_motion_attack_envelope_UNKNOWN')
    if any(p['normal'][1]for p in d['ports'].values()):raise ValueError('authored_vertical_boundary_clearance_not_yet_certified; native_port_matrix_retained')
    fs=samples();frames=[f for c in raw for f in fs.get((d['version'],c['id']),[])]
    if any(not fs.get((d['version'],c['id']))for c in raw):raise ValueError('fresh_source_direction_witness_missing')
    dx=phase;dy=334-base['entry_port'][1]+vertical_phase;c=translate(base,dx,dy);platforms=c['platforms'];edits=[];ps={};points={};port_indices={}
    for key,p in d['ports'].items():
        x,y=p['position'][0]+dx,p['position'][1]+dy
        idx=next((i for i,r in enumerate(platforms)if abs(r[1]-y-18)<1.1 and r[0]<=x-11 and x+11<=r[0]+r[2]),None)
        if idx is None:raise ValueError('port_ground_support_unknown/'+key)
        port_indices[key]=idx
    # Different heights are preserved and quantized only at terminal support.
    by_support={}
    for k,idx in port_indices.items():by_support.setdefault(idx,[]).append(k)
    for idx,keys in by_support.items():
        r=platforms[idx];wanted=[round((d['ports'][k]['position'][1]+dy-78)/128)*128+78 for k in keys]
        if len(set(wanted))!=1:raise ValueError('one_bank_requires_incompatible_port_heights')
        delta=wanted[0]+18-r[1]
        if abs(delta)>32.0001:raise ValueError('terminal_height_adjustment_exceeds_one_tile')
        if delta and any(t['platform_index']==idx for t in c.get('thorns',[])):raise ValueError('terminal_height_change_would_move_hazard')
        bottom=r[1]+r[3];before=r[:];r[1]+=delta;r[3]=bottom-r[1]
        if r[3]<=0:raise ValueError('terminal_bank_destroyed')
        if delta:edits.append(dict(kind='bank_top',index=idx,before=before,after=r[:],delta=delta))
    constraints={}
    for k,p in d['ports'].items():
        r=platforms[port_indices[k]];x=p['position'][0]+dx;normal=p['normal'][0];y=r[1]-18
        # Choose an actual terrain face, never a second connector platform.
        face=(math.floor((x-24)/128)*128 if normal<0 else math.ceil((x+24)/128)*128)
        dockx=face-normal*24
        if not r[0]-terminal_budget<=dockx-12 or dockx+12>r[0]+r[2]+terminal_budget:raise ValueError('port_terminal_span_requires_more_than_one_tile/'+k)
        constraints.setdefault(port_indices[k],[]).append((normal,face))
        cell=[int(face/128)if normal<0 else int(face/128)-1,int((y-78)/128)]
        points[k]=[dockx,y];ps[k]=dict(cell=cell,edge='W'if normal<0 else'E')
    for idx,values in constraints.items():
        r=platforms[idx];before=r[:];left=max([v for n,v in values if n<0],default=r[0]);right=min([v for n,v in values if n>0],default=r[0]+r[2]);left=min(left,r[0])if not any(n<0 for n,_ in values)else left
        if left-r[0]<-terminal_budget or right-(r[0]+r[2])>terminal_budget:raise ValueError('terminal_extension_exceeds_one_tile')
        if right-left<24:raise ValueError('terminal_ports_conflict_on_same_bank')
        if any(t['platform_index']==idx for t in c.get('thorns',[]))and(left!=r[0]or right!=r[0]+r[2]):raise ValueError('terminal_cut_changes_required_hazard')
        r[0]=left;r[2]=right-left
        if r!=before:edits.append(dict(kind='bank_boundary',index=idx,before=before,after=r[:]))
    # Remove only proven unvisited, non-serving catch banks. Multi-route return
    # cases contribute their actual deepest frames and protect their floor.
    ymax=max(f['y']+18+dy for f in frames);remove={i for i,r in enumerate(platforms)if r[1]>ymax+80 and r[2]>500 and i not in port_indices.values()}
    remove-={t['platform_index']for t in c.get('thorns',[])}
    remap={i:j for j,i in enumerate(i for i in range(len(platforms))if i not in remove)};c['platforms']=[r for i,r in enumerate(platforms)if i not in remove];c['one_way_platform_indices']=[remap[i]for i in c.get('one_way_platform_indices',[])if i not in remove];c['wall_platform_indices']=[remap[i]for i in c.get('wall_platform_indices',[])if i not in remove]
    for t in c.get('thorns',[]):t['platform_index']=remap[t['platform_index']]
    # Open only a narrow, non-hazardous terminal endcap intersecting the
    # declared Port aperture. Controlled gates and challenge hazards stay intact.
    for k,pt in points.items():
        face=ps[k]['cell'][0]*128 if ps[k]['edge']=='W'else(ps[k]['cell'][0]+1)*128
        body=[pt[0]-12,pt[1]-18,24,36]
        for j,r in enumerate(c['platforms']):
            if j==remap[port_indices[k]]:continue
            overlap=min(body[0]+body[2],r[0]+r[2])>max(body[0],r[0]) and min(body[1]+body[3],r[1]+r[3])>max(body[1],r[1])
            boundary=abs((r[0]if ps[k]['edge']=='W'else r[0]+r[2])-face)<.1
            if not overlap or not boundary or r[2]>32:continue
            if any(t['platform_index']==j for t in c.get('thorns',[])):raise ValueError('port_aperture_requires_removing_hazard')
            top=pt[1]-46
            if top<=r[1]:raise ValueError('port_aperture_requires_deleting_nonterminal_solid')
            before=r[:];r[3]=top-r[1];edits.append(dict(kind='terminal_endcap_aperture',index=j,before=before,after=r[:],port=k))
    ports={k:port(c,k,v['cell'],v['edge'],points[k])for k,v in ps.items()}
    # Existing play policies target the original authored endpoint, which must
    # remain supported; adapt endpoint markers, not its action sequence.
    transitions={};origins={};options={}
    for source,rel in zip(raw,d['relations']):
        a,b=rel['from'],rel['to'];old=translate(source,dx,dy);end=points[b];start=points[a]
        start_actual=[old['entry_port'][0],points[a][1]];end_actual=[old['exit_port'][0],points[b][1]]
        program=[dict(kind='walk',target=target(c,start_actual,'source-start/'+source['id']),budget_ticks=360),dict(kind='module',target=target(c,end_actual,'source-result/'+source['id']),control_plan=old['control_plan'],budget_ticks=3600),dict(kind='walk',target=target(c,end,'port-arrival/'+b),budget_ticks=360)]
        # Retarget final persistent settle to the new terminal state. Earlier
        # command coordinates and all mechanism timings remain unchanged.
        settling=[op for op in program[1]['control_plan']if op['op']=='settle']
        if not settling:raise ValueError('source_policy_has_no_stable_exit_settle')
        settling[-1]['target_x']=end_actual[0]
        key=a+'>'+b
        options.setdefault(key,[]).append(dict(program=program,case_id=source['id'],features=rel['features']))
        if key in transitions:continue
        transitions[key]=program;origins[key]=dict(source_version=d['version'],case_id=source['id'],features=rel['features'],parent_world_sha256=rel['world_sha256'])
    c['ports']=[dict(id=k,position=p['dock']['position'],normal=p['normal'],support_index=p['dock']['support_indices'][0])for k,p in ports.items()]
    for site in c.get('reward_sites',[]):
        original_y=site['position'][1]
        original=translate(base,dx,dy)
        idx=next((i for i,r in enumerate(original['platforms'])if abs(r[1]-original_y-18)<1.1 and r[0]<=site['position'][0]<=r[0]+r[2]),None)
        if idx in remap:
            delta=c['platforms'][remap[idx]][1]-original['platforms'][idx][1];site['position'][1]+=delta
            if site.get('region'):site['region'][1]+=delta
        site['target']=target(c,site['position'],site['id'])
    c['shop_sites']=[]
    center_key=d['relations'][0]['from'];center=ports[center_key]['dock']
    # Semantic centre is only an entry marker. Intermediate movement consumes
    # direct ordered pair programs; never assumes all Ports meet at this point.
    c.update(spawn=center['position'][:],entry_port=center['position'][:],exit_port=points[d['relations'][0]['to']][:],control_plan=[])
    rects=c['platforms'];width=max(r[0]+r[2]for r in rects);xs=[r[0]for r in rects];ys=[r[1]for r in rects]
    m=dict(id='native-content',case=c,ports=ports,center=copy.deepcopy(center),core=None,core_visit_program=[],port_to_center={},center_to_port={},port_transitions=transitions,
        transition_sources=origins,transition_options=options,center_port=center_key,functional_roles=['traversal']+(['junction']if len(ports)>2 else[]),boundary_gates=[],action_clearance=[[f['x']+dx-12,f['y']+dy-18,24,36]for f in frames[::2]],
        motion_contract=dict(mode='grounded_dock',capabilities=base['capabilities'][:],entry_grounded=True,required_air_shots=1,maximum_entry_speed=1),
        spec=dict(id='whole-library/'+d['version'],node_id='native-content',node=dict(id='native-content',role='challenge'),space=dict(core_bounds=[min(xs),min(ys),width,max(r[1]+r[3]for r in rects)-min(ys)]),placement=[0,0],ports=list(ports.values())),
        adaptation=dict(source_version=d['version'],terminal_edits=edits,terminal_bank_budget=terminal_budget,vertical_phase=vertical_phase,source_normals=old_normals,normal_adaptations=normal_overrides or{},removed_unvisited_catch_indices=sorted(remove),source_physics_inherited=False,map_added_platforms=0),
        source_version=d['version'],variant_id='content/'+d['version'][7:19]+'/phase'+str(phase)+'/v'+str(vertical_phase)+'/norm'+digest(normal_overrides or{})[:6]+'/bank'+str(terminal_budget),selection_family=d['family'],source_shape_sha256=digest(c['platforms']))
    cells=set().union(*(raster(r)for r in regions(m)))
    if not connected(cells):
        from .reservation import connect
        cells,added=connect(cells,ports);m['adaptation']['empty_reserved_blocks_added']=added
    m=declare(m,cells);errors=validate(m)
    if errors:raise ValueError(','.join(errors))
    c=m['case'];rr=regions(m);xmin=min(r[0]for r in rr);ymin=min(r[1]for r in rr);xmax=max(r[0]+r[2]for r in rr);ymax=max(r[1]+r[3]for r in rr);c['world_bounds']=[xmin-128,ymin-128,xmax-xmin+256,ymax-ymin+256]
    m['content_version']='sha256:'+digest(dict(case=c,ports=m['ports'],port_transitions=transitions));return m
