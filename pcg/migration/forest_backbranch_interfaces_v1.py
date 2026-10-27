"""Natural TOP/LEFT interfaces for two pinned original backbranch Modules.

All original nine platforms, original hooks/pickups/abilities and the complete
v11 H/R source prefix stay exact. No outward floor extends the source walk-off
edge. This is data adaptation on the existing native Godot Harness.
"""
from __future__ import annotations
import copy
import math
import shutil
from pathlib import Path
from . import core,boundary_runtime,godot_package,corners,forest_departure_v11 as original
from .adaptation import _append_platform,_extent,NON_GEOMETRY
from pcg.prototype.factory.core.quality import digest

purpose=original.purpose
RUNNER_SCRIPT=original.RUNNER_SCRIPT
SOURCE_DEPENDENCIES=[Path(__file__),*original.SOURCE_DEPENDENCIES]


def _settle(x):return dict(op='settle',trigger=dict(after=0),target_x=x,deadband=.6,source_native_gain=5.5)


def _wait_goal(rect,timeout=480,ready=False):
    trigger=dict(state='grounded',migration_goal=rect,timeout=timeout)
    if ready:trigger['migration_drop_ready']=True
    return dict(op='wait',trigger=trigger)


def adapt(document,input_cases,original_document,original_cases):
    if len(input_cases)!=1 or len(original_cases)!=1:raise ValueError('backbranch_adapter_requires_one_pinned_source_route')
    doc=copy.deepcopy(document);case=copy.deepcopy(input_cases[0]);source_case=original_cases[0]
    gc=doc['generationContract'];size=gc['foundation']['blockSize'];raw=case['source_behavior']
    if raw.get('main_route_kind',raw.get('chain_contract',{}).get('departure_before_first_hook'))not in('air_chain','outside_drop'):
        raise ValueError('not_the_pinned_outside_drop_backbranch_relation')
    if [a['action']for a in case['source_action_program']]!=['H','R']:raise ValueError('original_HR_sequence_required')
    source_ids={o['id']for o in original_document['objects']}
    # Keep source Cells with their current exact native behavior metadata, plus
    # genuine original pickup consumers installed by the frozen native binder.
    doc['objects']=[copy.deepcopy(o)for o in doc['objects']if o['id']in source_ids or '/original-pickup-'in o['id']]
    if not source_ids<={o['id']for o in doc['objects']}:raise ValueError('original_source_cell_missing')
    case['platforms']=copy.deepcopy(source_case['platforms'])
    case['one_way_platform_indices']=copy.deepcopy(source_case.get('one_way_platform_indices',[]))
    case['wall_platform_indices']=copy.deepcopy(source_case.get('wall_platform_indices',[]))
    case.pop('recorded_frames',None);case.pop('module_sha256',None);case.pop('factory_evidence',None)
    original_goal=source_case['goal']
    cut=next((i for i,c in enumerate(case['control_plan'])if c.get('op')=='wait'and c.get('trigger',{}).get('migration_goal')==original_goal and c['trigger'].get('timeout')==1200),None)
    if cut is None:raise ValueError('original_v11_program_tail_boundary_not_found')
    prefix=copy.deepcopy(case['control_plan'][:cut])
    if not any(c.get('op')=='wait'and c.get('trigger',{}).get('source_min_y')==case['hooks'][0]['y']+20 and c['trigger'].get('state')=='free'for c in prefix):
        raise ValueError('real_original_descending_cast_observer_missing')
    entry=next(p for p in gc['ports']if p['id']==case['route_spec']['from_port'])
    exit_port=next(p for p in gc['ports']if p['id']==case['route_spec']['to_port'])
    source_ports={p['id']:p for p in original_document['generationContract']['ports']}
    crown=next(o for o in doc['objects']if o['id']==source_ports[exit_port['id']]['support']['objectId'])
    crown_floor=crown['y'];spawn=case['spawn']
    xmin,ymin,xmax,ymax=_extent(original_document,[source_case])
    xphase=(spawn[0]-64)%size;yphase=(crown_floor-96)%size
    bx=xphase+math.floor((xmin-xphase)/size)*size;by=yphase+math.floor((ymin-yphase)/size)*size
    w=math.ceil((xmax-bx)/size)*size;h=math.ceil((ymax-by)/size)*size
    if crown['x']-bx<80:bx-=size;w+=size
    bounds=dict(x=bx,y=by,w=w,h=h);gc['space']['bounds']=bounds
    gc['foundation'].update(widthBlocks=int(w/size),heightBlocks=int(h/size))
    gc['space']['occupancy']['objectIds']=[o['id']for o in doc['objects']if o['type']not in NON_GEOMETRY]
    gc['space']['occupancy']['regions']=[]
    gc['composition']['cells']=[c for c in gc['composition']['cells']if all(oid in{o['id']for o in doc['objects']}for oid in c['objectIds'])]
    # Top landing is vertically separated from the original walk-off bank.
    top_rect=[spawn[0]-32,by+64,64,12]
    obj,top_index=_append_platform(doc,[case],entry['objectId'].rsplit('/',1)[0]+'/natural-top-entry',top_rect,True)
    entry.update(position=[spawn[0],by],normal=[0,-1],face='TOP',surface='ONE_WAY_PLATFORM',permission='INOUT',
        stagingPosition=[spawn[0],top_rect[1]-18],support=dict(objectId=obj['id'],face='top',status='source_derived'))
    # The original western 80px mouth passes the full 24x36 body. Put the
    # short new shore in that existing opening, never across the inner H/R gap.
    left_rect=[bx,crown_floor,64,24]
    obj,left_index=_append_platform(doc,[case],exit_port['objectId'].rsplit('/',1)[0]+'/natural-left-exit',left_rect)
    inner=bx+64
    if crown['x']>inner:_append_platform(doc,[case],exit_port['objectId'].rsplit('/',1)[0]+'/western-mouth-approach',[inner,crown_floor,crown['x']-inner,24])
    exit_port.update(position=[bx,crown_floor-32],normal=[-1,0],face='LEFT',surface='ROCK',permission='INOUT',
        stagingPosition=[bx+24,crown_floor-18],support=dict(objectId=obj['id'],face='top',status='source_derived'))
    for port,index in ((entry,top_index),(exit_port,left_index)):
        x,y=port['position'];marker=next(o for o in doc['objects']if o['id']==port['objectId'])
        marker['x']=x-marker['w']/2;marker['y']=y-marker['h']/2
        runtime=next(p for p in case['ports']if p['id']==port['id'])
        runtime.update(position=copy.deepcopy(port['stagingPosition']),normal=copy.deepcopy(port['normal']),support_index=index)
        case.setdefault('block_ports',{})[port['id']]=dict(id=port['id'],position=[x,y],normal=port['normal'],stagingPosition=port['stagingPosition'],aperture=[x-32,y-32,64,64])
    target=exit_port['stagingPosition'];tail=[_wait_goal(original_goal,1200),_settle(target[0]),_wait_goal([target[0]-5,target[1]-4,10,8])]
    # Keep an explicit final settle for the existing continuous-exit fixture.
    tail.append(_settle(target[0]))
    case['control_plan']=prefix+tail;case['goal']=[target[0]-8,target[1]-5,16,10];case['exit_port']=list(target)
    case['id']+='-natural-top-left-v1';case['max_frames']=3000
    ingress=[_settle(spawn[0]),dict(op='drop_through',trigger=dict(after=1)),
        _wait_goal([spawn[0]-5,top_rect[1]-23,10,10],360,ready=True),
        dict(op='drop_through',trigger=dict(after=1)),_settle(spawn[0])]
    case['migration_boundary_plans']={entry['id']:dict(ingress=ingress)}
    case['migration_boundary_continuations']={entry['id']:dict(ingress=ingress),exit_port['id']:dict(egress=tail)}
    case['generation_rule']['registration_source']='pcg/migration/forest_backbranch_interfaces_v1.py'
    case['migration_adaptation']=dict(schema='pcg/original-backbranch-natural-interfaces/v1',originalCorePlatformCount=len(source_case['platforms']),originalCorePlatformsExact=True,
        originalHRPrefixSha256=digest(prefix),originalHRProgramPrefixExact=True,noFloorAcrossOriginalWalkoff=True)
    case.pop('migration_boundary_control_binding',None)
    world=case['world_bounds'];left=min(world[0],bx-128);top=min(world[1],by-128);right=max(world[0]+world[2],bx+w+128);bottom=max(world[1]+world[3],by+h+128)
    case['world_bounds']=[left,top,right-left,bottom-top]
    ports={p['id']:p for p in gc['ports']}
    for route in gc['routes']:route['localDisplacementBlocks']=[(z-a)/size for a,z in zip(ports[route['from']]['position'],ports[route['to']]['position'])]
    for v in gc['validations']:v.update(result='UNKNOWN',artifacts=[],method='pending_actual_original_backbranch_top_left_interfaces')
    gc['generation']['migration']['backbranchNaturalInterfaces']=dict(schema='pcg/original-backbranch-natural-interfaces/v1',
        originalCorePlatformsExact=True,originalHooksAndRewardsPreserved=True,originalCapabilities=case['capabilities'],
        originalHRPrefixSha256=digest(prefix),sourcePrefixCommands=len(prefix),sourceDescendingCastThreshold=case['hooks'][0]['y']+20,
        newEntryFace='TOP',newExitFace='LEFT',reason='Remove artificial horizontal shore which prevented the original outside drop; use original western body opening.',validation='UNKNOWN')
    return doc,[case],gc['generation']['migration']['backbranchNaturalInterfaces']


def prepare(folder,out):
    folder=Path(folder).resolve();out=Path(out).resolve()
    if out.exists():raise ValueError('new_interface_output_already_exists')
    doc=core.read(folder/'module.mapnote.json');cases=core.read(folder/'cases.json')['cases'];meta=core.read(folder/'migration.json');source=core.REPO/meta['sourcePath']
    doc,cases,receipt=adapt(doc,cases,core.read(source/'module.mapnote.json'),core.read(source/'cases.json')['cases'])
    doc=godot_package.bind_case_behavior(doc,cases);doc,cases,bindings=boundary_runtime.bind(doc,cases);corners.annotate(doc)
    shutil.copytree(folder,out)
    for name in('replay-cases.json','physics-input-cases.json','physics.json','package.json'):(out/name).unlink(missing_ok=True)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases));core.write(out/'natural-interface-repair.json',receipt);core.write(out/'boundary-bindings.json',bindings)
    for key in('physicsReport','boundaryProbe','godotLoad'):meta.pop(key,None)
    meta.update(status='prepared_unverified',internalGeometryChanged=True,evidence=[],unresolved=['Real original descending H/R, natural top/left body crossings, cheap bypasses, resources and native consumer validation pending.'])
    meta['adaptation']=receipt;core.write(out/'migration.json',meta)
    result=core.contract(out/'module.mapnote.json',refresh=True);godot_package.audit_cases(core.read(out/'module.mapnote.json'),cases,require_replay=False)
    return dict(status='prepared_unverified',folder=core.relative(out),contract=result)
