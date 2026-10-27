"""Versioned repairs which leave authored core coordinates and programs exact.

Outer interfaces are independent landing zones. Historical unverified face
proposals may be replaced by the nearest natural outflow; this never grants a
route or certificate without a new actual experiment.
"""
from pathlib import Path
import copy
import math
from . import core
from .adaptation import _append_platform, NON_GEOMETRY

CORE_FIELDS=('platforms','spawn','entry_port','exit_port','goal','control_plan','moving_platforms',
    'latches','enemies','hooks','hazards','thorns','saws','reward_sites','one_way_platform_indices',
    'wall_platform_indices','required_carrier_park','world_cell_sources','expected_reward','required_rewards')


def _restore(document,input_cases,original_document,original_cases):
    if len(input_cases)!=len(original_cases):raise ValueError('core_restore_route_count_changed')
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases)
    doc['objects']=copy.deepcopy(original_document['objects'])
    for case,source in zip(cases,original_cases):
        if case['id']!=source['id']:raise ValueError('core_restore_case_order_changed')
        for key in CORE_FIELDS:
            if key in source:case[key]=copy.deepcopy(source[key])
            else:case.pop(key,None)
        for key in ('recorded_frames','factory_evidence','module_sha256'):case.pop(key,None)
        case['ports']=copy.deepcopy(source.get('ports',[]))
        case['block_ports']={}
    gc=doc['generationContract']
    gc.pop('internalWaypoints',None)
    gc['space']['occupancy']['objectIds']=[o['id']for o in doc['objects']if o['type']not in NON_GEOMETRY]
    gc['space']['occupancy']['regions']=[]
    gc['composition']['cells']=[c for c in gc['composition']['cells']if all(any(o['id']==oid for o in doc['objects'])for oid in c['objectIds'])]
    return doc,cases


def _command(op,**kwargs):return dict(op=op,trigger=dict(after=0),**kwargs)


def _grounded_goal(goal,timeout=600):
    return dict(op='wait',trigger=dict(state='grounded',migration_goal=list(goal),timeout=timeout))


def _port_support(source_port,source_case,source_doc):
    runtime=next((p for p in source_case.get('ports',[])if p['id']==source_port['id']),None)
    if runtime and 'support_index'in runtime:return runtime['support_index']
    obj=next(o for o in source_doc['objects']if o['id']==source_port['support']['objectId'])
    rectangle=[obj[k]for k in ('x','y','w','h')]
    return next(i for i,r in enumerate(source_case['platforms'])if r==rectangle)


def bottom_pocket(document,input_cases,original_document,original_cases,port_id,*,window_depth=None,short_local_ingress=False,multiple_routes=False,through_lower_floors=False,moving_park_clearance=False):
    """Open an actual downward OWP outlet below an enclosed lower reward pocket.

    Every original core rectangle, bell, gate, reward, spawn, and command stays
    at its original coordinates. The lower landing receives a one-way material
    window and side solid backing; the top landing behavior remains identical.
    No long tunnel through the intact upper banks is fabricated.
    """
    doc,cases=_restore(document,input_cases,original_document,original_cases)
    gc=doc['generationContract'];b=gc['space']['bounds'];size=gc['foundation']['blockSize']
    source_ports={p['id']:p for p in original_document['generationContract']['ports']}
    primary=next(p for p in gc['ports']if p['id']==cases[0]['route_spec']['from_port'])
    primary_index=_port_support(source_ports[primary['id']],original_cases[0],original_document)
    phase=(original_cases[0]['platforms'][primary_index][1]-96)%size
    geometry=[o for o in doc['objects']if o['type']not in NON_GEOMETRY]
    ymin=min(o['y']for o in geometry);ymax=max(o['y']+o['h']for o in geometry)
    b['y']=phase+math.floor((ymin-phase)/size)*size
    b['h']=math.ceil((ymax-b['y'])/size)*size
    gc['foundation']['heightBlocks']=int(b['h']/size)
    for interface in gc['ports']:
        if interface['normal'][0]:
            si=_port_support(source_ports[interface['id']],original_cases[0],original_document)
            floor=original_cases[0]['platforms'][si][1]
            canonical=b['y']+96+round((floor-b['y']-96)/size)*size
            interface['position'][1]=canonical-32
            interface['stagingPosition'][1]=canonical-18
    target=next(p for p in gc['ports']if p['id']==port_id)
    source_port=source_ports[port_id]
    index=_port_support(source_port,original_cases[0],original_document)
    pocket=copy.deepcopy(original_cases[0]['platforms'][index]);center=source_port.get('grid',{}).get('stagingPosition',source_port['position'])
    if pocket[2]<96:raise ValueError('bottom_pocket_too_narrow_for_body_window')
    column=max(0,min(gc['foundation']['widthBlocks']-1,round((center[0]-b['x'])/size-.5)))
    px=b['x']+(column+.5)*size;py=b['y']+b['h']
    # The original low landing is not moved. Only its local support material
    # changes; source collision rectangle index and top stay exactly the same.
    host=next(o for o in doc['objects']if o['id']==source_port['support']['objectId'])
    if host['type']not in ('terrain','platform')or host.get('trackId'):
        raise ValueError('bottom_pocket_requires_static_authored_landing')
    if any(o.get('hostId')==host['id']for o in doc['objects']):
        raise ValueError('bottom_pocket_hazard_host_requires_separate_design')
    host['type']='platform';host['sourceIndex']=index
    depth=pocket[3]if window_depth is None else window_depth
    if not 8<=depth<=pocket[3]:raise ValueError('invalid_pocket_material_window_depth')
    host['h']=depth
    for case in cases:case['platforms'][index][3]=depth
    for case in cases:
        if index not in case.setdefault('one_way_platform_indices',[]):case['one_way_platform_indices'].append(index)
    width=min(128,pocket[2]-24)
    window_left=max(pocket[0]+12,min(center[0]-width/2,pocket[0]+pocket[2]-12-width))
    if moving_park_clearance:window_left=pocket[0]+pocket[2]-12-width
    window_right=window_left+width
    if not window_left+12<=px<=window_right-12:
        raise ValueError('bottom_block_center_outside_safe_local_pocket_window')
    backing=[]
    for label,rect in [('left',[pocket[0],pocket[1],window_left-pocket[0],pocket[3]]),
                       ('right',[window_right,pocket[1],pocket[0]+pocket[2]-window_right,pocket[3]])]:
        if rect[2]>.01:
            obj,new_index=_append_platform(doc,cases,host['id']+'-window-'+label,rect)
            backing.append(dict(objectId=obj['id'],platformIndex=new_index,rect=rect))
    inside_floor=py-18
    if inside_floor<=pocket[1]+24:
        raise ValueError('bottom_outlet_has_insufficient_vertical_landing_space')
    windows=[dict(index=index,floor=pocket[1],rect=pocket)]
    if through_lower_floors:
        for lower_index,lower in enumerate(original_cases[0]['platforms']):
            if lower_index==index or not pocket[1]<lower[1]<inside_floor-24:continue
            if not lower[0]+12<=px<=lower[0]+lower[2]-12:continue
            if lower[2]<96 or lower[3]>128:raise ValueError('bottom_column_hits_original_wall:'+str(lower_index))
            lower_host=next((o for o in doc['objects']if o['type']in('terrain','platform')and[o.get(k)for k in('x','y','w','h')]==lower),None)
            if lower_host is None or lower_host.get('trackId'):raise ValueError('bottom_column_hits_unmapped_core_cell:'+str(lower_index))
            if any(o.get('hostId')==lower_host['id']for o in doc['objects']):raise ValueError('bottom_column_hazard_host_requires_design')
            lower_host['type']='platform';lower_host['h']=12;lower_host['sourceIndex']=lower_index
            for case in cases:
                case['platforms'][lower_index][3]=12
                if lower_index not in case.setdefault('one_way_platform_indices',[]):case['one_way_platform_indices'].append(lower_index)
            lower_width=min(128,lower[2]-24);wl=max(lower[0]+12,min(px-lower_width/2,lower[0]+lower[2]-12-lower_width));wr=wl+lower_width
            for label,piece in [('left',[lower[0],lower[1],wl-lower[0],lower[3]]),('right',[wr,lower[1],lower[0]+lower[2]-wr,lower[3]])]:
                if piece[2]>.01:_append_platform(doc,cases,lower_host['id']+'-bottom-window-'+label,piece)
            windows.append(dict(index=lower_index,floor=lower[1],rect=copy.deepcopy(lower)))
    windows.sort(key=lambda item:item['floor'])
    rect=[px-48,inside_floor,96,12]
    obj,dock_index=_append_platform(doc,cases,target['objectId'].rsplit('/',1)[0]+'/bottom-outlet-'+port_id,rect,True)
    target.update(position=[px,py],normal=[0,1],face='BOTTOM',surface='ONE_WAY_PLATFORM',
        stagingPosition=[px,inside_floor-18],support=dict(objectId=obj['id'],face='top',status='source_derived'))
    target.pop('cornerRelocations',None)
    docks={port_id:dict(index=dock_index,rect=rect,sourceIndex=index,sourceFloor=pocket[1])}
    # Other side interfaces get independent flat boundary landing zones. Their
    # original core banks never have their top quantized to the outer grid.
    for port in gc['ports']:
        if port['id']==port_id:continue
        original=source_ports[port['id']];support_index=_port_support(original,original_cases[0],original_document)
        shore=original_cases[0]['platforms'][support_index]
        nx=port['normal'][0]
        if not nx:raise ValueError('other_vertical_port_requires_explicit_original_core_adapter')
        floor=port['stagingPosition'][1]+18
        edge=port['position'][0]
        dock=[edge if nx<0 else edge-64,floor,64,24]
        obj,new_index=_append_platform(doc,cases,port['objectId'].rsplit('/',1)[0]+'/core-preserved-dock-'+port['id'],dock)
        docks[port['id']]=dict(index=new_index,rect=dock,sourceIndex=support_index,sourceFloor=shore[1])
        port.update(support=dict(objectId=obj['id'],face='top',status='source_derived'),surface='ROCK')
        inner=edge-nx*64
        start,end=(inner,shore[0]+24)if nx<0 else(shore[0]+shore[2]-24,inner)
        if end>start:
            connector=[start,shore[1],end-start,24]
            _append_platform(doc,cases,port['objectId'].rsplit('/',1)[0]+'/core-preserved-approach-'+port['id'],connector)
        # Side docking height changes are handled after the original goal,
        # never by moving the original bank, bell, reward, or source spawn.
    for port in gc['ports']:
        data=docks[port['id']];marker=next(o for o in doc['objects']if o['id']==port['objectId'])
        marker['x']=port['position'][0]-marker['w']/2;marker['y']=port['position'][1]-marker['h']/2
        x,y=port['position']
        for case in cases:
            runtime=next((p for p in case['ports']if p['id']==port['id']),None)
            if runtime is None:runtime=dict(id=port['id']);case['ports'].append(runtime)
            runtime.update(position=copy.deepcopy(port['stagingPosition']),normal=copy.deepcopy(port['normal']),support_index=data['index'])
            case['block_ports'][port['id']]=dict(id=port['id'],position=[x,y],normal=copy.deepcopy(port['normal']),
                stagingPosition=copy.deepcopy(port['stagingPosition']),aperture=[x-32,y-32,64,64])
    stabilizers=[]
    for case,source in zip(cases,original_cases):
        if not any(op.get('op')=='settle'for op in case['control_plan']):
            # The existing fixture builder needs a declared terminal settle.
            # Preserve every original command as a prefix; nominal goal-stable
            # playback can finish before this harmless alignment is reached.
            command=_command('settle',target_x=source['goal'][0]+source['goal'][2]/2,deadband=3)
            case['control_plan'].append(command)
            stabilizers.append(dict(caseId=case['id'],added=command,originalProgramPrefixExact=True))
        route=case['route_spec'];entry=next(p for p in gc['ports']if p['id']==route['from_port'])
        if route['to_port']!=port_id:
            if not multiple_routes:raise ValueError('bottom_pocket_repair_only_declared_lower_outflow_routes')
            destination=next(p for p in gc['ports']if p['id']==route['to_port'])
            plan=_side_egress(source,destination,docks[destination['id']])
        else:
            original_goal=source['goal'];core_x=px;core_y=pocket[1]-18
            plan=copy.deepcopy(source['control_plan'])+[_grounded_goal(original_goal,source.get('max_frames',1200))]
            departure_x=(pocket[0]+pocket[2]-26)if moving_park_clearance else core_x
            plan += [_command('settle',target_x=departure_x,deadband=2),
                     _grounded_goal([departure_x-3,core_y-4,6,8],240),
                     dict(op='drop_through',trigger=dict(after=1))]
            if moving_park_clearance:
                if len(windows)<2:raise ValueError('moving_support_clearance_needs_actual_lower_floor')
                safe_x=pocket[0]+pocket[2]-6;first_lower=windows[1]
                plan += [_command('settle',target_x=safe_x,deadband=2),
                         _grounded_goal([first_lower['rect'][0],first_lower['floor']-23,first_lower['rect'][2],10],600)]
            for lower in windows[1:]:
                plan += [_command('settle',target_x=px,deadband=2),
                    dict(op='wait',trigger=dict(state='grounded',migration_goal=[px-5,lower['floor']-23,10,10],migration_drop_ready=True,timeout=600)),
                    dict(op='drop_through',trigger=dict(after=1))]
            plan += [_command('settle',target_x=px,deadband=2),
                dict(op='wait',trigger=dict(state='grounded',migration_goal=[px-8,inside_floor-23,16,10],migration_drop_ready=True,timeout=600)),
                dict(op='drop_through',trigger=dict(after=1)),_command('settle',target_x=px,deadband=2)]
        ingress=_side_ingress(source,entry,docks[entry['id']])
        case['migration_boundary_plans']={entry['id']:dict(ingress=ingress),route['to_port']:dict(egress=plan)}
        if short_local_ingress and route['to_port']==port_id:
            case['migration_boundary_plans'][port_id]['local_ingress']=[_command('settle',target_x=px,deadband=2),
                dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=6)),
                _grounded_goal([px-8,inside_floor-23,16,10],240)]
        case['migration_adaptation']=dict(schema='pcg/original-core-preserving/v1',
            originalCoreRectanglesExact=(depth==pocket[3]and not through_lower_floors),originalCoreTopSurfacesExact=True,originalProgramExact=True,portAdaptations=[])
        case['max_frames']=max(source.get('max_frames',1200),1200)
        world=case.get('world_bounds',[-1200,-1200,4000,4000]);left=min(world[0],b['x']-128);top=min(world[1],b['y']-128)
        right=max(world[0]+world[2],b['x']+b['w']+128);bottom=max(world[1]+world[3],b['y']+b['h']+128)
        case['world_bounds']=[left,top,right-left,bottom-top]
    by_port={p['id']:p for p in gc['ports']}
    for route in gc['routes']:
        route['localDisplacementBlocks']=[(z-a)/size for a,z in zip(by_port[route['from']]['position'],by_port[route['to']]['position'])]
    for validation in gc['validations']:validation.update(result='UNKNOWN',artifacts=[],method='pending_original_core_preserving_revalidation')
    gc['space']['occupancy']['regions']=[]
    gc['generation']['migration']['corePreservingRepair']=dict(kind='bottom_pocket',
        sourcePortId=port_id,sourceUnverifiedNormal=source_port['normal'],normal=[0,1],surface='ONE_WAY_PLATFORM',
        originalCoreRectanglesExact=(depth==pocket[3]and not through_lower_floors),originalCoreTopSurfacesExact=True,originalProgramExact=True,originalRewardsExact=True,
        additionalWindowPlatforms=[w['index']for w in windows[1:]],movingSupportClearance=moving_park_clearance,
        localMaterialWindow=dict(platformIndex=index,rect=pocket,collisionDepth=depth,window=[window_left,pocket[1],width,pocket[3]],backing=backing),
        terminalStabilizers=stabilizers,originalProgramPrefixExact=True,
        reason='Nearest natural downward outflow; avoids a long safe tunnel through the intact upper bank.',validation='UNKNOWN')
    if stabilizers:gc['generation']['migration']['corePreservingRepair']['originalProgramExact']=False
    return doc,cases,gc['generation']['migration']['corePreservingRepair']


def _side_egress(source,port,dock):
    nx=port['normal'][0];boundary=port['position'][0]
    floor=dock['sourceFloor'];outside=boundary+nx*48;inside=boundary-nx*24
    approach=boundary-nx*100
    program=copy.deepcopy(source['control_plan'])+[_grounded_goal(source['goal'],source.get('max_frames',1200))]
    program += [_command('settle',target_x=approach,deadband=2),_grounded_goal([approach-4,floor-23,8,10],360),
                _command('settle',target_x=inside,deadband=2)]
    if dock['rect'][1]<floor-.1:
        if 'jump'not in source.get('capabilities',[]):raise ValueError('side_dock_upstep_requires_original_jump_ability')
        program += [dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=16))]
    program += [_grounded_goal([inside-5,dock['rect'][1]-23,10,10],300),_command('settle',target_x=outside,deadband=2)]
    return program


def _side_ingress(source,port,dock):
    nx=port['normal'][0];boundary=port['position'][0];inside=boundary-nx*24;inner=boundary-nx*112
    program=[_command('settle',target_x=inside,deadband=2),_grounded_goal([inside-5,dock['rect'][1]-23,10,10],240)]
    if abs(dock['sourceFloor']-dock['rect'][1])>.1:
        program.append(_command('settle',target_x=inner,deadband=2))
        if dock['sourceFloor']<dock['rect'][1]:
            if 'jump'not in source.get('capabilities',[]):raise ValueError('side_entry_upstep_requires_original_jump_ability')
            program += [dict(op='jump',trigger=dict(after=1)),dict(op='jump_release',trigger=dict(after=16))]
        program.append(_grounded_goal([inner-5,dock['sourceFloor']-23,10,10],300))
    program.append(_command('settle',target_x=source['spawn'][0],deadband=2))
    return program


def side_interfaces(document,input_cases,original_document,original_cases,*,face_overrides=None):
    """Independent side docks, with original core floors and commands untouched.

    This first general repair intentionally rejects an intervening original
    collider in the body corridor instead of cutting a new safe lane through it.
    Such interfaces need a natural alternative face, not a fake geometry pass.
    """
    face_overrides=face_overrides or {}
    doc,cases=_restore(document,input_cases,original_document,original_cases)
    gc=doc['generationContract'];b=gc['space']['bounds'];size=gc['foundation']['blockSize']
    source_ports={p['id']:p for p in original_document['generationContract']['ports']}
    primary_id=cases[0]['route_spec']['from_port'];primary_index=_port_support(source_ports[primary_id],original_cases[0],original_document)
    phase=(original_cases[0]['platforms'][primary_index][1]-96)%size
    geometry=[o for o in doc['objects']if o['type']not in NON_GEOMETRY]
    ymin=min(o['y']for o in geometry);ymax=max(o['y']+o['h']for o in geometry)
    b['y']=phase+math.floor((ymin-phase)/size)*size;b['h']=math.ceil((ymax-b['y'])/size)*size
    gc['foundation']['heightBlocks']=int(b['h']/size)
    docks={};records=[]
    for port in gc['ports']:
        face=face_overrides.get(port['id'],port.get('face'))
        if face not in ('LEFT','RIGHT'):raise ValueError('independent_side_adapter_requires_side_face:'+port['id'])
        nx=-1 if face=='LEFT'else 1
        source_index=_port_support(source_ports[port['id']],original_cases[0],original_document)
        shore=original_cases[0]['platforms'][source_index];floor=shore[1]
        value=(floor-b['y']-96)/size
        # A no-jump Module gets a downward exit dock, not a new mandatory jump.
        row=round(value)if all('jump'in c.get('capabilities',[])for c in original_cases)else math.ceil(value)
        canonical=b['y']+96+row*size
        edge=b['x']if nx<0 else b['x']+b['w'];anchor=[edge,canonical-32]
        dock=[edge if nx<0 else edge-64,canonical,64,24]
        inner=edge-nx*64
        start,end=(inner,shore[0]+24)if nx<0 else(shore[0]+shore[2]-24,inner)
        # Detect a real body obstruction, never silently carve critical walls.
        corridor=[min(inner,shore[0]if nx<0 else shore[0]+shore[2]),floor-40,
                  abs(inner-(shore[0]if nx<0 else shore[0]+shore[2])),40]
        blocked=[]
        for i,rect in enumerate(original_cases[0]['platforms']):
            if i==source_index:continue
            if min(corridor[0]+corridor[2],rect[0]+rect[2])>max(corridor[0],rect[0])and min(floor,rect[1]+rect[3])>max(floor-40,rect[1]):blocked.append(i)
        if blocked:raise ValueError('original_core_blocks_proposed_side_interface:'+port['id']+':'+','.join(map(str,blocked)))
        obj,index=_append_platform(doc,cases,port['objectId'].rsplit('/',1)[0]+'/independent-side-dock-'+port['id'],dock)
        if end>start:_append_platform(doc,cases,port['objectId'].rsplit('/',1)[0]+'/original-floor-approach-'+port['id'],[start,floor,end-start,24])
        old_normal=copy.deepcopy(port['normal'])
        port.update(position=anchor,normal=[nx,0],face=face,surface='ROCK',stagingPosition=[edge-nx*24,canonical-18],
                    support=dict(objectId=obj['id'],face='top',status='source_derived'))
        docks[port['id']]=dict(index=index,rect=dock,sourceFloor=floor)
        records.append(dict(portId=port['id'],oldNormal=old_normal,normal=[nx,0],originalFloor=floor,dockFloor=canonical,
            originalCoreRectanglesExact=True,interfaceOnlyHeightChange=canonical-floor,validation='UNKNOWN'))
        marker=next(o for o in doc['objects']if o['id']==port['objectId'])
        marker['x']=anchor[0]-marker['w']/2;marker['y']=anchor[1]-marker['h']/2
        for case in cases:
            runtime=next((p for p in case['ports']if p['id']==port['id']),None)
            if runtime is None:runtime=dict(id=port['id']);case['ports'].append(runtime)
            runtime.update(position=port['stagingPosition'],normal=[nx,0],support_index=index)
            case['block_ports'][port['id']]=dict(id=port['id'],position=anchor,normal=[nx,0],
                stagingPosition=port['stagingPosition'],aperture=[anchor[0]-32,anchor[1]-32,64,64])
    ports={p['id']:p for p in gc['ports']}
    for case,source in zip(cases,original_cases):
        route=case['route_spec'];a=ports[route['from_port']];z=ports[route['to_port']]
        case['migration_boundary_plans']={a['id']:dict(ingress=_side_ingress(source,a,docks[a['id']])),z['id']:dict(egress=_side_egress(source,z,docks[z['id']]))}
        case['migration_adaptation']=dict(schema='pcg/original-core-preserving/v1',originalCoreRectanglesExact=True,originalProgramExact=True,portAdaptations=[])
        world=case.get('world_bounds',[-1200,-1200,4000,4000]);left=min(world[0],b['x']-128);top=min(world[1],b['y']-128)
        right=max(world[0]+world[2],b['x']+b['w']+128);bottom=max(world[1]+world[3],b['y']+b['h']+128)
        case['world_bounds']=[left,top,right-left,bottom-top];case['max_frames']=max(case.get('max_frames',1200),1200)
    for route in gc['routes']:route['localDisplacementBlocks']=[(z-a)/size for a,z in zip(ports[route['from']]['position'],ports[route['to']]['position'])]
    for validation in gc['validations']:validation.update(result='UNKNOWN',artifacts=[],method='pending_original_core_side_dock_revalidation')
    receipt=dict(schema='pcg/original-core-independent-side-docks/v1',ports=records,
        originalCoreRectanglesExact=True,originalRewardsExact=True,originalProgramExact=True,validation='UNKNOWN')
    gc['generation']['migration']['corePreservingRepair']=receipt
    return doc,cases,receipt


def restore_core_shores(document,input_cases,original_document,original_cases):
    """Repair imported replay-authoritative modules without changing their core.

    Current boundary anchors are kept when a 64px dock fits outside the old bank.
    Otherwise that side expands by one Block; no raised connector is inserted
    inside the last original reward/goal landing pixels. Frozen recorded inputs
    remain the caller's authority. Returned boundary continuations are TAILS,
    not replacements for those original source replay inputs.
    """
    from pcg.prototype.factory.core.quality import digest
    doc,cases=_restore(document,input_cases,original_document,original_cases)
    gc=doc['generationContract'];b=gc['space']['bounds'];size=gc['foundation']['blockSize']
    source_ports={p['id']:p for p in original_document['generationContract']['ports']}
    preserved=[]
    for case,current in zip(cases,input_cases):
        # Importers may have installed an exact original-source frame replay
        # after their initial placeholder plan was decoded. Do not discard it.
        for key in ('recorded_frames','control_plan','native_replay','source_replay','original_replay','source_identity'):
            if key in current:case[key]=copy.deepcopy(current[key])
        preserved.append(dict(caseId=case['id'],recordedFrames=len(case.get('recorded_frames',[])),
            recordedFramesSha256=digest(case.get('recorded_frames',[])),controlPlanSha256=digest(case.get('control_plan',[]))))
    expansions=[]
    for direction in (-1,1):
        candidates=[p for p in gc['ports']if p['normal'][0]==direction]
        if not candidates:continue
        required=[]
        for port in candidates:
            i=_port_support(source_ports[port['id']],original_cases[0],original_document)
            shore=original_cases[0]['platforms'][i]
            edge=b['x']if direction<0 else b['x']+b['w']
            length=shore[0]-edge if direction<0 else edge-shore[0]-shore[2]
            required.append(max(0,80-length))
        blocks=math.ceil(max(required)/size)
        if blocks:
            shift=blocks*size
            if direction<0:b['x']-=shift
            b['w']+=shift
            expansions.append(dict(face='LEFT'if direction<0 else'RIGHT',blocks=blocks,pixels=shift,
                reason='Fit body-clear independent boundary dock outside original bank and original replay goal.'))
    gc['foundation']['widthBlocks']=int(b['w']/size)
    docks={};records=[]
    for port in gc['ports']:
        nx=port['normal'][0]
        if not nx:raise ValueError('import_replay_shore_repair_requires_horizontal_port:'+port['id'])
        i=_port_support(source_ports[port['id']],original_cases[0],original_document)
        shore=original_cases[0]['platforms'][i];edge=b['x']if nx<0 else b['x']+b['w']
        floor=port['stagingPosition'][1]+18
        dock=[edge if nx<0 else edge-64,floor,64,24]
        inside_edge=edge-nx*64
        # Preserve the entire old endpoint footprint. The extension begins at
        # its true outer edge, not 24px inside the original goal landing zone.
        start,end=(inside_edge,shore[0])if nx<0 else(shore[0]+shore[2],inside_edge)
        if end<start:raise ValueError('no_external_space_for_independent_boundary_dock')
        if end>start:_append_platform(doc,cases,port['objectId'].rsplit('/',1)[0]+'/replay-shore-approach-'+port['id'],[start,shore[1],end-start,24])
        obj,index=_append_platform(doc,cases,port['objectId'].rsplit('/',1)[0]+'/replay-independent-dock-'+port['id'],dock)
        port.update(position=[edge,port['position'][1]],stagingPosition=[edge-nx*24,floor-18],
            surface='ROCK',support=dict(objectId=obj['id'],face='top',status='source_derived'))
        marker=next(o for o in doc['objects']if o['id']==port['objectId'])
        marker['x']=port['position'][0]-marker['w']/2;marker['y']=port['position'][1]-marker['h']/2
        docks[port['id']]=dict(index=index,rect=dock,sourceFloor=shore[1])
        for case in cases:
            rp=next((p for p in case['ports']if p['id']==port['id']),None)
            if rp is None:rp=dict(id=port['id']);case['ports'].append(rp)
            rp.update(position=port['stagingPosition'],normal=copy.deepcopy(port['normal']),support_index=index)
            x,y=port['position'];case['block_ports'][port['id']]=dict(id=port['id'],position=[x,y],normal=port['normal'],stagingPosition=port['stagingPosition'],aperture=[x-32,y-32,64,64])
        records.append(dict(portId=port['id'],originalSupportIndex=i,originalFloor=shore[1],dockFloor=floor,
            supportIndex=index,boundary=port['position'],oldFootprintPreserved=True,validation='UNKNOWN'))
    ports={p['id']:p for p in gc['ports']}
    for case,source in zip(cases,original_cases):
        route=case['route_spec'];a=ports[route['from_port']];z=ports[route['to_port']]
        full=_side_egress(source,z,docks[z['id']])
        tail=full[len(source['control_plan']):]
        case['migration_boundary_continuations']={a['id']:dict(ingress=_side_ingress(source,a,docks[a['id']])),z['id']:dict(egress=tail)}
        case['migration_core_replay_authority']=dict(kind='preserved_prepared_original_source_inputs',
            originalInputFrames=len(case.get('recorded_frames',[])),boundaryEgressPlanIsTailOnly=True,
            noResetBetweenOriginalReplayAndBoundary=True)
        world=case.get('world_bounds',[-1200,-1200,4000,4000]);left=min(world[0],b['x']-128);top=min(world[1],b['y']-128)
        right=max(world[0]+world[2],b['x']+b['w']+128);bottom=max(world[1]+world[3],b['y']+b['h']+128)
        case['world_bounds']=[left,top,right-left,bottom-top]
    for route in gc['routes']:route['localDisplacementBlocks']=[(z-a)/size for a,z in zip(ports[route['from']]['position'],ports[route['to']]['position'])]
    for validation in gc['validations']:validation.update(result='UNKNOWN',artifacts=[],method='pending_original_replay_core_shore_revalidation')
    receipt=dict(schema='pcg/imported-original-core-shore-repair/v1',originalCoreRectanglesExact=True,
        originalEntityAndRewardPositionsExact=True,sourceReplayInputAuthorityPreserved=preserved,
        boundaryExpansions=expansions,ports=records,validation='UNKNOWN',internalGeometryChanged=True)
    gc['generation']['migration']['corePreservingRepair']=receipt
    return doc,cases,receipt
