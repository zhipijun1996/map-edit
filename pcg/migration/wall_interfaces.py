"""Natural interfaces for a downward wall challenge inside an original cage.

The original core walls/platforms/abilities/commands stay unchanged. A local,
non-climbable entrance shaft prevents entering above the cage and bypassing it;
its walls stop above the original sampled core body envelope.
"""
import copy
import math
from .core_preserving import _restore,_port_support,_append_platform,_command,_grounded_goal,_side_egress
from .adaptation import _extent


def guided_top_entry(document,input_cases,original_document,original_cases,*,entry_id='entry',exit_id='exit'):
    doc,cases=_restore(document,input_cases,original_document,original_cases)
    gc=doc['generationContract'];size=gc['foundation']['blockSize'];source_ports={p['id']:p for p in original_document['generationContract']['ports']}
    if len(gc['ports'])!=2:raise ValueError('guided_cage_adapter_currently_requires_two_ports')
    if any(r['to']==entry_id for r in gc['routes']):raise ValueError('cannot_narrow_known_reverse_route_to_input')
    if any(c['spawn']!=original_cases[0]['spawn']for c in original_cases):raise ValueError('guided_cage_requires_one_common_initial_dock')
    if any('jump'in c.get('capabilities',[])or'shot_recoil'in c.get('capabilities',[])or'grapple'in c.get('capabilities',[])for c in original_cases):
        raise ValueError('top_input_rights_require_new_validation_for_upward_abilities')
    spawn=original_cases[0]['spawn']
    if any(c['goal'][1]+c['goal'][3]/2<spawn[1]+96 for c in original_cases):raise ValueError('guided_top_entry_would_bypass_upward_core_challenge')
    entry=next(p for p in gc['ports']if p['id']==entry_id);exit_port=next(p for p in gc['ports']if p['id']==exit_id)
    entry_index=_port_support(source_ports[entry_id],original_cases[0],original_document)
    exit_index=_port_support(source_ports[exit_id],original_cases[0],original_document)
    entry_floor=original_cases[0]['platforms'][entry_index][1];shore=original_cases[0]['platforms'][exit_index]
    xmin,ymin,xmax,ymax=_extent(original_document,original_cases)
    xphase=(spawn[0]-64)%size;yphase=(entry_floor-96)%size
    bx=xphase+math.floor((xmin-xphase)/size)*size;by=yphase+math.floor((ymin-yphase)/size)*size
    w=math.ceil((xmax-bx)/size)*size;h=math.ceil((ymax-by)/size)*size
    if shore[0]-bx<80:bx-=size;w+=size
    bounds=dict(x=bx,y=by,w=w,h=h);gc['space']['bounds']=bounds
    gc['foundation'].update(widthBlocks=int(w/size),heightBlocks=int(h/size))
    # Keep both new walls above every sampled original body rectangle.
    original_regions=original_document['generationContract']['space'].get('actionClearance',{}).get('regions',[])
    core_top=min([r['y']for r in original_regions]or[spawn[1]-18])
    shaft_bottom=min(spawn[1]-40,core_top-24)
    if shaft_bottom<=by+128:raise ValueError('insufficient_space_for_local_guided_top_interface')
    shaft=[]
    for label,x in [('left',spawn[0]-36),('right',spawn[0]+24)]:
        rect=[x,by,12,shaft_bottom-by]
        obj,index=_append_platform(doc,cases,entry['objectId'].rsplit('/',1)[0]+'/guided-shaft-'+label,rect)
        # Never add these connector walls to wall_platform_indices.
        shaft.append(dict(objectId=obj['id'],platformIndex=index,rect=rect,wallClimbable=False))
    top_rect=[spawn[0]-32,by+64,64,12]
    obj,top_index=_append_platform(doc,cases,entry['objectId'].rsplit('/',1)[0]+'/guided-top-dock',top_rect,True)
    caps=original_cases[0]['capabilities']
    entry.update(position=[spawn[0],by],normal=[0,-1],face='TOP',surface='ONE_WAY_PLATFORM',permission='INPUT',
        stagingPosition=[spawn[0],top_rect[1]-18],support=dict(objectId=obj['id'],face='top',status='source_derived'),
        initialPermissionConditions=dict(availableAbilitiesExact=copy.deepcopy(caps),requiresRevalidationWithAdditionalUpwardAbilities=True))
    value=(shore[1]-by-96)/size;floor=by+96+math.ceil(value)*size
    left_rect=[bx,floor,64,24]
    obj,left_index=_append_platform(doc,cases,exit_port['objectId'].rsplit('/',1)[0]+'/natural-left-dock',left_rect)
    inner=bx+64
    _append_platform(doc,cases,exit_port['objectId'].rsplit('/',1)[0]+'/old-floor-left-approach',[inner,shore[1],shore[0]+24-inner,24])
    exit_port.update(position=[bx,floor-32],normal=[-1,0],face='LEFT',surface='ROCK',permission='INOUT',
        stagingPosition=[bx+24,floor-18],support=dict(objectId=obj['id'],face='top',status='source_derived'))
    for port,index in ((entry,top_index),(exit_port,left_index)):
        x,y=port['position'];marker=next(o for o in doc['objects']if o['id']==port['objectId'])
        marker['x']=x-marker['w']/2;marker['y']=y-marker['h']/2
        for case in cases:
            runtime=next((p for p in case['ports']if p['id']==port['id']),None)
            if runtime is None:runtime=dict(id=port['id']);case['ports'].append(runtime)
            runtime.update(position=copy.deepcopy(port['stagingPosition']),normal=copy.deepcopy(port['normal']),support_index=index)
            case['block_ports'][port['id']]=dict(id=port['id'],position=[x,y],normal=port['normal'],stagingPosition=port['stagingPosition'],aperture=[x-32,y-32,64,64])
    for case,source in zip(cases,original_cases):
        ingress=[_command('settle',target_x=spawn[0],deadband=2),dict(op='drop_through',trigger=dict(after=1)),
            dict(op='wait',trigger=dict(state='grounded',migration_goal=[spawn[0]-5,top_rect[1]-23,10,10],migration_drop_ready=True,timeout=360)),
            dict(op='drop_through',trigger=dict(after=1)),_command('settle',target_x=source['spawn'][0],deadband=2)]
        egress=_side_egress(source,exit_port,dict(sourceFloor=shore[1],rect=left_rect))
        case['migration_boundary_plans']={entry_id:dict(ingress=ingress),exit_id:dict(egress=egress)}
        case['migration_adaptation']=dict(schema='pcg/original-core-preserving/v1',originalCoreRectanglesExact=True,originalProgramExact=True,portAdaptations=[])
        world=case.get('world_bounds',[-1200,-1200,4000,4000]);l=min(world[0],bx-128);t=min(world[1],by-128)
        r=max(world[0]+world[2],bx+w+128);bottom=max(world[1]+world[3],by+h+128)
        case['world_bounds']=[l,t,r-l,bottom-t]
    ports={p['id']:p for p in gc['ports']}
    for route in gc['routes']:route['localDisplacementBlocks']=[(z-a)/size for a,z in zip(ports[route['from']]['position'],ports[route['to']]['position'])]
    for validation in gc['validations']:validation.update(result='UNKNOWN',artifacts=[],method='pending_natural_top_input_cage_revalidation')
    receipt=dict(schema='pcg/guided-top-input-original-cage/v1',originalCoreRectanglesExact=True,
        originalProgramExact=True,originalAbilitiesExact=copy.deepcopy(caps),
        entry=dict(portId=entry_id,originalUnverifiedNormal=source_ports[entry_id]['normal'],normal=[0,-1],permission='INPUT',shaft=shaft),
        exit=dict(portId=exit_id,originalUnverifiedNormal=source_ports[exit_id]['normal'],normal=[-1,0],sourceFloor=shore[1],dockFloor=floor),
        scope='Initial rights certified only for exact source ability set; additional upward abilities require independent interface validation.',validation='UNKNOWN')
    gc['generation']['migration']['corePreservingRepair']=receipt
    return doc,cases,receipt
