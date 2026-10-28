"""Minimal candidate revision for an unverified under-ledge exit orientation.

An extended RIGHT receiving floor catches the very fall meant to require a
braking shot. Reusing the nearer LEFT bank preserves the original pocket; only
historically proposed (not measured) outward directions may use this adapter.
"""
from pathlib import Path
import copy
import shutil
from . import core


def underledge_left(source,out):
    source,out=Path(source),Path(out)
    if out.exists():raise ValueError('repair_candidate_exists')
    doc=core.read(source/'module.mapnote.json');cases=core.read(source/'cases.json')['cases']
    if len(cases)!=1 or cases[0]['family']!='brake-under-ledge':raise ValueError('only_registered_single_underledge_repair')
    gc=doc['generationContract'];case=cases[0];route=case['route_spec']
    port=next(p for p in gc['ports']if p['id']==route['to_port'])
    if port['face']!='RIGHT'or'not evidence'not in port.get('orientationSource',''):
        raise ValueError('requires_original_unverified_right_orientation')
    adaptation=core.read(source/'adaptation.json')
    binding=next(p for p in adaptation['portAdaptations']if p['portId']==port['id'])
    index=binding['after']['supportIndex'];host_id=port['support']['objectId']
    host=next(o for o in doc['objects']if o['id']==host_id)
    core_floor=next((r for r in case['platforms']if r[0]<=case['goal'][0]+case['goal'][2]/2<=r[0]+r[2]
                    and abs((r[1]-18)-(case['goal'][1]+case['goal'][3]/2))<10),None)
    if core_floor is None:raise ValueError('actual_reward_pocket_support_missing')
    bx=gc['space']['bounds']['x'];floor=core_floor[1]
    before=copy.deepcopy(port);old_rect=list(case['platforms'][index])
    rect=[bx,floor,core_floor[0]+24-bx,24]
    if rect[2]<=0:raise ValueError('left_connector_has_no_positive_span')
    for key,value in zip(('x','y','w','h'),rect):host[key]=value
    case['platforms'][index]=rect
    position=[bx,floor-32];staging=[bx+24,floor-18]
    port.update(position=position,stagingPosition=staging,normal=[-1,0],face='LEFT',
        orientationSource='migration revision: nearer LEFT bank; original RIGHT was an unverified design proposal and caught the core fall')
    marker=next(o for o in doc['objects']if o['id']==port['objectId'])
    marker['x'],marker['y']=position[0]-marker['w']/2,position[1]-marker['h']/2
    runtime=next(p for p in case['ports']if p['id']==port['id'])
    runtime.update(position=staging,normal=[-1,0],support_index=index)
    case['block_ports'][port['id']].update(position=position,stagingPosition=staging,
        normal=[-1,0],aperture=[position[0]-32,position[1]-32,64,64],crossing_offset=[24,14])
    binding['after'].update(position=position,stagingPosition=staging)
    receipt=dict(schema='pcg/underledge-port-orientation-repair/v1',source=core.relative(source),
        reason='RIGHT connector placed a broad receiving floor under the core fall; a nearer LEFT outlet preserves original recoil-braking purpose.',
        originalOutwardDirection='unverified proposal; no measured permission removed',
        portId=port['id'],before=dict(position=before['position'],face=before['face'],connector=old_rect),
        after=dict(position=position,face='LEFT',connector=rect),validation='UNKNOWN')
    adaptation.setdefault('repairs',[]).append(receipt)
    case['migration_adaptation']=copy.deepcopy(case['migration_adaptation'])
    case['migration_adaptation']['portAdaptations']=copy.deepcopy(adaptation['portAdaptations'])
    case['migration_adaptation']['repairs']=copy.deepcopy(adaptation['repairs'])
    ports={p['id']:p for p in gc['ports']}
    for r in gc['routes']:
        r['localDisplacementBlocks']=[(b-a)/128 for a,b in zip(ports[r['from']]['position'],ports[r['to']]['position'])]
    gc['generation']['migration']['orientationRepair']=receipt
    from .corners import annotate
    annotate(doc)
    out.mkdir(parents=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',{'cases':cases})
    core.write(out/'adaptation.json',adaptation)
    meta=core.read(source/'migration.json');meta['adaptation']=adaptation;meta['status']='prepared_unverified'
    meta['evidence']=[];meta.pop('physicsReport',None)
    core.write(out/'migration.json',meta)
    if(source/'components').exists():shutil.copytree(source/'components',out/'components')
    core.contract(out/'module.mapnote.json',refresh=True)
    return dict(status='prepared_unverified',out=str(out),repair=receipt)


def top_full_body_dock(source,out):
    """A TOP landing must place the complete body inside the Module."""
    source,out=Path(source),Path(out)
    if out.exists():raise ValueError('repair_candidate_exists')
    doc=core.read(source/'module.mapnote.json');cases=core.read(source/'cases.json')['cases']
    gc=doc['generationContract'];bounds=gc['space']['bounds'];repairs=[]
    for port in gc['ports']:
        if port['face']!='TOP':continue
        if port['surface']!='ONE_WAY_PLATFORM':raise ValueError('top_dock_requires_actual_one_way')
        runtime=next(p for p in cases[0]['ports']if p['id']==port['id'])
        index=runtime['support_index'];old=list(cases[0]['platforms'][index])
        if index not in cases[0].get('one_way_platform_indices',[]):raise ValueError('top_support_is_not_runtime_one_way')
        desired=bounds['y']+48;delta=desired-old[1]
        if abs(delta)>16.01:raise ValueError('outside_registered_minimal_top_dock_shift')
        new=[old[0],desired,old[2],old[3]]
        host=next(o for o in doc['objects']if o['id']==port['support']['objectId'])
        host['y']=desired;port['stagingPosition']=[port['position'][0],desired-18]
        for case in cases:
            if case['platforms'][index]!=old:raise ValueError('top_support_geometry_disagrees_between_routes')
            case['platforms'][index]=list(new)
            live=next(p for p in case['ports']if p['id']==port['id'])
            live['position']=list(port['stagingPosition'])
            block=case['block_ports'][port['id']]
            block['stagingPosition']=list(port['stagingPosition']);block['crossing_offset']=[0,30]
            adaptation=case.get('migration_adaptation',{})
            for entry in adaptation.get('portAdaptations',[]):
                if entry['portId']!=port['id']:continue
                entry['after']['stagingPosition']=list(port['stagingPosition'])
                for connector in entry.get('connectorPlatforms',[]):
                    if connector['platformIndex']==index:connector['rect']=list(new)
        repairs.append(dict(portId=port['id'],platformIndex=index,objectId=host['id'],before=old,after=new,
            reason='Old TOP dock put body center14px inside; complete36px body still straddled boundary. Dock is now30px inside, leaving12px head clearance inside rectangle.',
            body=[24,36],physicsChanged=False,geometryChanged=True,validation='UNKNOWN'))
    if not repairs:raise ValueError('no_registered_top_dock')
    gc['generation']['migration']['topFullBodyDockRepair']=repairs
    from .corners import annotate
    annotate(doc)
    out.mkdir(parents=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',{'cases':cases})
    adaptation=core.read(source/'adaptation.json');adaptation.setdefault('repairs',[]).extend(repairs)
    core.write(out/'adaptation.json',adaptation)
    meta=core.read(source/'migration.json');meta['adaptation']=adaptation;meta['status']='prepared_unverified'
    meta['evidence']=[];meta.pop('physicsReport',None)
    core.write(out/'migration.json',meta)
    if(source/'components').exists():shutil.copytree(source/'components',out/'components')
    core.contract(out/'module.mapnote.json',refresh=True)
    return dict(status='prepared_unverified',out=str(out),repairs=repairs)
