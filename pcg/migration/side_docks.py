"""Explicit local ROCK docks for side OWP interfaces that fail body tolerance.

This is a versioned repair operation, not a blanket change to all one-way Cells.
The original interior one-way platform remains; only the boundary landing zone
gets a real solid collider and declares its changed ROCK surface honestly.
"""
import copy


def repair(document, input_cases, port_ids, *, width=64, thickness=24):
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases)
    gc=doc['generationContract'];b=gc['space']['bounds'];receipts=[]
    if not 48<=width<=128 or not 8<=thickness<=32:
        raise ValueError('local_side_dock_size_out_of_range')
    if len(set(port_ids))!=len(port_ids):raise ValueError('duplicate_side_dock_port')
    for identifier in port_ids:
        port=next((p for p in gc['ports']if p['id']==identifier),None)
        if port is None:raise ValueError('unknown_side_dock_port:'+identifier)
        if port.get('face')not in ('LEFT','RIGHT') or port.get('surface')!='ONE_WAY_PLATFORM':
            raise ValueError('side_dock_repair_requires_side_one_way_port:'+identifier)
        nx=port['normal'][0];x=port['position'][0];floor=port['stagingPosition'][1]+18
        rect=[x if nx<0 else x-width,floor,width,thickness]
        if rect[0]<b['x'] or rect[0]+width>b['x']+b['w'] or floor<b['y'] or floor+thickness>b['y']+b['h']:
            raise ValueError('side_dock_would_leave_module_rectangle:'+identifier)
        oid=port['objectId'].rsplit('/',1)[0]+'/solid-side-dock-'+identifier
        if any(o['id']==oid for o in doc['objects']):raise ValueError('side_dock_already_materialized:'+identifier)
        index=len(cases[0]['platforms'])
        obj=dict(id=oid,type='terrain',x=rect[0],y=rect[1],w=rect[2],h=rect[3],rotation=0,
            sourceIndex=index,label='Certified repair pending: solid Port dock',
            note='Local ROCK landing zone; original interior one-way platform retained')
        doc['objects'].append(obj)
        gc['space']['occupancy']['objectIds'].append(oid)
        gc['composition']['cells'].append(dict(id='solid-side-dock-'+identifier,contentVersion='sha256:'+'0'*64,objectIds=[oid]))
        original_support=copy.deepcopy(port['support'])
        port.update(surface='ROCK',support=dict(objectId=oid,face='top',status='source_derived'))
        for case in cases:
            if len(case['platforms'])!=index:raise ValueError('side_dock_route_geometry_count_disagrees')
            case['platforms'].append(list(rect))
            runtime_port=next(p for p in case['ports']if p['id']==identifier)
            runtime_port['support_index']=index
            if identifier in case.get('block_ports',{}):
                case['block_ports'][identifier]['surface']='ROCK'
                case['block_ports'][identifier]['supportIndex']=index
            case.pop('recorded_frames',None)
            case.pop('module_sha256',None)
            case.setdefault('migration_side_docks',[]).append(dict(portId=identifier,platformIndex=index,rect=rect,
                previousSurface='ONE_WAY_PLATFORM',surface='ROCK',validation='UNKNOWN'))
        receipts.append(dict(portId=identifier,previousSurface='ONE_WAY_PLATFORM',surface='ROCK',
            previousSupport=original_support,supportObjectId=oid,platformIndex=index,rect=rect,
            preservesInteriorOneWayPlatform=True,reason='Actual one-way boundary ±2px body penetration failed; new solid dock requires revalidation.',
            validation='UNKNOWN'))
    for validation in gc['validations']:
        validation.update(result='UNKNOWN',artifacts=[],method='pending_local_solid_side_dock_revalidation')
    for route in gc['routes']:route['availability']='UNKNOWN'
    gc.setdefault('generation',{}).setdefault('migration',{})['localSideDockAdaptations']=receipts
    return doc,cases,dict(schema='pcg/local-solid-side-dock-repair/v1',internalGeometryChanged=True,
        rows=receipts,validation='UNKNOWN',certificateInherited=False)
