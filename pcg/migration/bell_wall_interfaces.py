"""Restore the original bell ray with a natural right entrance.

The original left-facing bell sits beneath the tiny starting bank. A left
connector blocks that actual projectile path. This repair instead opens a local
48px body window in the right wall, preserving its real upper/lower climb faces,
and puts the approach bridge to the right of the original gun position.
"""
import copy
import math
from .core_preserving import _restore,_port_support,_append_platform,_side_ingress,_side_egress
from .adaptation import _extent


def right_entry(document,input_cases,original_document,original_cases,*,entry_id='entry',exit_id='exit'):
    doc,cases=_restore(document,input_cases,original_document,original_cases);gc=doc['generationContract'];size=gc['foundation']['blockSize']
    source_ports={p['id']:p for p in original_document['generationContract']['ports']}
    entry_index=_port_support(source_ports[entry_id],original_cases[0],original_document)
    exit_index=_port_support(source_ports[exit_id],original_cases[0],original_document)
    bank=original_cases[0]['platforms'][entry_index];left_bank=original_cases[0]['platforms'][exit_index];floor=bank[1]
    walls=[(i,r)for i,r in enumerate(original_cases[0]['platforms'])if i!=entry_index and r[0]>bank[0]+bank[2]and r[2]<=64 and r[1]<floor-48<r[1]+r[3]]
    if len(walls)!=1:raise ValueError('one_unique_right_wall_required_for_local_entry_window')
    wi,wall=walls[0]
    if wi not in original_cases[0].get('wall_platform_indices',[]):raise ValueError('original_right_wall_was_not_climbable')
    wall_obj=next(o for o in doc['objects']if o['type']=='terrain'and[o.get(k)for k in('x','y','w','h')]==wall)
    if any(o.get('hostId')==wall_obj['id']for o in doc['objects']):raise ValueError('cannot_cut_hazard_host_wall')
    top=[wall[0],wall[1],wall[2],floor-48-wall[1]];lower=[wall[0],floor,wall[2],wall[1]+wall[3]-floor]
    if min(top[3],lower[3])<=0:raise ValueError('entry_window_would_remove_original_upper_or_lower_wall')
    for key,value in zip(('x','y','w','h'),top):wall_obj[key]=value
    for case in cases:case['platforms'][wi]=list(top)
    lower_obj,lower_index=_append_platform(doc,cases,wall_obj['id']+'-lower-entry-window',lower)
    lower_obj['wallClimbable']=True
    for case in cases:case.setdefault('wall_platform_indices',[]).append(lower_index)
    xmin,ymin,xmax,ymax=_extent(original_document,original_cases);bx=math.floor(xmin/size)*size
    phase=(floor-96)%size;by=phase+math.floor((ymin-phase)/size)*size
    w=math.ceil((xmax-bx)/size)*size;h=math.ceil((ymax-by)/size)*size
    if bx+w-wall[0]-wall[2]<80:w+=size
    if left_bank[0]-bx<80:bx-=size;w+=size
    b=dict(x=bx,y=by,w=w,h=h);gc['space']['bounds']=b;gc['foundation'].update(widthBlocks=int(w/size),heightBlocks=int(h/size))
    entry=next(p for p in gc['ports']if p['id']==entry_id);exit_port=next(p for p in gc['ports']if p['id']==exit_id)
    # The bridge lies to the right of the original player/gun. Nothing is
    # inserted under the original down-left projectile launch and bell ray.
    bridge=[bank[0]+bank[2],floor,wall[0]-bank[0]-bank[2],24]
    _append_platform(doc,cases,entry['objectId'].rsplit('/',1)[0]+'/right-internal-approach',bridge)
    right=bx+w;right_dock=[right-64,floor,64,24]
    _append_platform(doc,cases,entry['objectId'].rsplit('/',1)[0]+'/right-external-approach',[wall[0]+wall[2],floor,right-64-wall[0]-wall[2],24])
    obj,entry_dock_index=_append_platform(doc,cases,entry['objectId'].rsplit('/',1)[0]+'/right-boundary-dock',right_dock)
    entry.update(position=[right,floor-32],normal=[1,0],face='RIGHT',surface='ROCK',permission='INOUT',
        stagingPosition=[right-24,floor-18],support=dict(objectId=obj['id'],face='top',status='source_derived'))
    exit_floor=by+96+math.ceil((left_bank[1]-by-96)/size)*size
    left_dock=[bx,exit_floor,64,24]
    _append_platform(doc,cases,exit_port['objectId'].rsplit('/',1)[0]+'/old-floor-left-approach',[bx+64,left_bank[1],left_bank[0]+24-bx-64,24])
    obj,exit_dock_index=_append_platform(doc,cases,exit_port['objectId'].rsplit('/',1)[0]+'/left-boundary-dock',left_dock)
    exit_port.update(position=[bx,exit_floor-32],normal=[-1,0],face='LEFT',surface='ROCK',permission='INOUT',
        stagingPosition=[bx+24,exit_floor-18],support=dict(objectId=obj['id'],face='top',status='source_derived'))
    for port,index in ((entry,entry_dock_index),(exit_port,exit_dock_index)):
        x,y=port['position'];marker=next(o for o in doc['objects']if o['id']==port['objectId'])
        marker['x']=x-marker['w']/2;marker['y']=y-marker['h']/2
        for case in cases:
            runtime=next((p for p in case['ports']if p['id']==port['id']),None)
            if runtime is None:runtime=dict(id=port['id']);case['ports'].append(runtime)
            runtime.update(position=port['stagingPosition'],normal=port['normal'],support_index=index)
            case['block_ports'][port['id']]=dict(id=port['id'],position=[x,y],normal=port['normal'],stagingPosition=port['stagingPosition'],aperture=[x-32,y-32,64,64])
    for case,source in zip(cases,original_cases):
        case['migration_boundary_plans']={entry_id:dict(ingress=_side_ingress(source,entry,dict(sourceFloor=floor,rect=right_dock))),
            exit_id:dict(egress=_side_egress(source,exit_port,dict(sourceFloor=left_bank[1],rect=left_dock)))}
        world=case.get('world_bounds',[-1200,-1200,4000,4000]);l=min(world[0],bx-128);t=min(world[1],by-128)
        r=max(world[0]+world[2],bx+w+128);bottom=max(world[1]+world[3],by+h+128)
        case['world_bounds']=[l,t,r-l,bottom-t]
    ports={p['id']:p for p in gc['ports']}
    for route in gc['routes']:route['localDisplacementBlocks']=[(z-a)/size for a,z in zip(ports[route['from']]['position'],ports[route['to']]['position'])]
    for validation in gc['validations']:validation.update(result='UNKNOWN',artifacts=[],method='pending_actual_right_entry_bell_ray_preservation')
    receipt=dict(schema='pcg/bell-wall-natural-right-entry/v1',entryNormal=[1,0],exitNormal=[-1,0],
        originalProgramExact=True,originalAbilitiesExact=copy.deepcopy(original_cases[0]['capabilities']),
        originalBellGateRewardPosesExact=True,originalStartingBankExact=True,
        wallWindow=dict(originalIndex=wi,before=wall,upper=top,lower=lower,opening=[wall[0],floor-48,wall[2],48],preservedWallClimbableIndices=[wi,lower_index]),
        newApproach=bridge,projectilePhysicsUnchanged=True,validation='UNKNOWN')
    gc['generation']['migration']['corePreservingRepair']=receipt
    return doc,cases,receipt
