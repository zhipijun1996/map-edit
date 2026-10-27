"""Keep existing Macro cores exact and add independent local outer docks.

The right interfaces are separate landing zones, not a bridge across the
authored brake fall. Movement programs for these gaps use the existing player
and input DSL through the existing boundary-runtime wrapper.
"""
import argparse
import copy
import json
from pathlib import Path

from . import core, corners
from .adaptation import NON_GEOMETRY, _append_platform, persist_macro_components
from .boundary_runtime import bind


def cmd(op,after=0,**values):return dict(op=op,trigger=dict(after=after),**values)


def ground_goal(x,y,width=8,timeout=300):
    return dict(op='wait',trigger=dict(state='grounded',migration_goal=[x-width/2,y-4,width,8],timeout=timeout))


def wait_x(value,direction='gte',state=None):
    trigger=dict(dynamic=dict(kind='actor_x',direction=direction,value=value),timeout=300)
    if state:trigger['state']=state
    return dict(op='wait',trigger=trigger)


def _ingress(port_id,target,lip):
    x,y=target
    if port_id=='A':return[cmd('settle',target_x=x,deadband=2)]
    # Start outside the actual Port, dock, and jump back across the empty
    # separation. The high ceiling ends before the local boundary dock.
    return[cmd('settle',target_x=940,deadband=2),ground_goal(940,420 if port_id=='C'else 676),
        cmd('settle',target_x=x,deadband=2),cmd('jump'),cmd('jump_release',20),
        wait_x(800,'lte','descending'),cmd('shoot',direction=[1,0]),
        cmd('settle',target_x=x,deadband=2)]


def _egress(source,port_id,lip,launch):
    plan=copy.deepcopy(source['control_plan'])
    goal=source['goal']
    plan.append(dict(op='wait',trigger=dict(state='grounded',migration_goal=goal,timeout=600)))
    if port_id=='A':return plan+[cmd('settle',target_x=-304,deadband=2)]
    start_x=680 if port_id=='C'else launch
    start_y=420 if port_id=='C'else source['exit_port'][1]
    plan += [cmd('settle',target_x=start_x,deadband=2),ground_goal(start_x,start_y),
             cmd('settle',target_x=972,deadband=2),cmd('jump'),cmd('jump_release',16 if port_id=='C'else 20)]
    if port_id=='B':plan.append(wait_x(lip+16,'gte','airborne'))
    direction=[-1,0]if port_id=='C'else[-0.9404258001104552,0.34]
    floor=420 if port_id=='C'else 676
    return plan+[cmd('shoot',direction=direction),cmd('settle',target_x=972,deadband=2),
                 ground_goal(972,floor),cmd('settle',target_x=1072,deadband=2)]


def prepare(prefix,out):
    if not 12<=len(prefix)<=64 or any(c not in'0123456789abcdef'for c in prefix):
        raise ValueError('macro_source_prefix_requires_at_least_twelve_hex_digits')
    direct=list(core.LEGACY.glob(prefix+'*'));journal=core.ledger()
    if len(direct)==1:
        source=direct[0];reference=core.relative(source)
    else:
        matches=[(name,entry)for name,entry in journal['entries'].items()
            if name.startswith(core.relative(core.LEGACY)+'/')and entry.get('sourceVersion','').removeprefix('sha256:').startswith(prefix)]
        if len(matches)!=1:raise ValueError('ambiguous_or_missing_original_macro_source')
        reference,entry=matches[0];source=core.resolve_artifact(reference+'/record.json').parent
    drafts=list((core.REPO/'.cache/migration/full-v7').glob(prefix+'*'))
    prepared=drafts[0]if len(drafts)==1 else core.REPO/journal['entries'][reference]['destination']
    out=Path(out).resolve()
    if out.exists():raise ValueError('macro_repair_destination_exists')
    if out.is_relative_to(core.ACTIVE)or out.is_relative_to(core.RECYCLE):raise ValueError('macro_repair_stage_outside_archive')
    original=core.read(source/'module.mapnote.json');original_cases=core.legacy_cases(source)
    doc=core.read(prepared/'module.mapnote.json');g=doc['generationContract']
    doc['objects']=copy.deepcopy(original['objects'])
    g['composition']=copy.deepcopy(original['generationContract']['composition'])
    cases=copy.deepcopy(original_cases)
    for case in cases:
        for key in ('recorded_frames','factory_evidence','module_sha256'):case.pop(key,None)
    rectangles=original_cases[0]['platforms']
    for o in doc['objects']:
        if o['type']in('terrain','platform')and not o.get('trackId'):
            o['sourceIndex']=next(i for i,r in enumerate(rectangles)if r==[o[k]for k in('x','y','w','h')])
    g['space']['occupancy']=dict(status='partial',coverage='Exact original core plus three independent local landing docks',
        objectIds=[o['id']for o in doc['objects']if o['type']not in NON_GEOMETRY],regions=[])
    source_ports={p['id']:p for p in original['generationContract']['ports']}
    dock_data={}
    for p in g['ports']:
        old=source_ports[p['id']];p['objectId']=old['objectId']
        face='LEFT'if p['id']=='A'else'RIGHT';normal=[-1,0]if face=='LEFT'else[1,0]
        floor=694 if p['id']=='B'else 438
        rect=[-256,438,120,24]if p['id']=='A'else[928,floor,96,24]
        obj,index=_append_platform(doc,cases,p['objectId'].rsplit('/',1)[0]+'/independent-outer-dock-'+p['id'],rect)
        p.update(face=face,normal=normal,position=[-256 if face=='LEFT'else 1024,floor-32],
            stagingPosition=[-232 if face=='LEFT'else 1000,floor-18],surface='ROCK',permission='INOUT',
            support=dict(objectId=obj['id'],face='top',status='source_derived'))
        marker=next(o for o in doc['objects']if o['id']==p['objectId'])
        marker.update(x=p['position'][0]-marker['w']/2,y=p['position'][1]-marker['h']/2)
        dock_data[p['id']]=dict(platformIndex=index,rect=rect)
    lip=rectangles[6][0]+rectangles[6][2]
    launch=rectangles[7][0]+rectangles[7][2]-16
    ports={p['id']:p for p in g['ports']}
    for case,source_case in zip(cases,original_cases):
        case['ports']=copy.deepcopy(source_case['ports']);case['block_ports']={}
        for p in g['ports']:
            native=next(v for v in case['ports']if v['id']==p['id'])
            native.update(position=p['stagingPosition'],normal=p['normal'],support_index=dock_data[p['id']]['platformIndex'])
            x,y=p['position'];case['block_ports'][p['id']]=dict(id=p['id'],position=[x,y],normal=p['normal'],
                stagingPosition=p['stagingPosition'],aperture=[x-32,y-32,64,64])
        route=source_case['route_spec']
        case['migration_boundary_plans']={
            route['from_port']:dict(ingress=_ingress(route['from_port'],source_case['spawn'],lip)),
            route['to_port']:dict(egress=_egress(source_case,route['to_port'],lip,launch))}
        case['migration_adaptation']=dict(schema='pcg/original-core-preserving/v1',originalCoreRectanglesExact=True,
            originalProgramExact=True,originalRewardsExact=True,portAdaptations=[])
        case['max_frames']=max(case['max_frames'],1800)
    for r in g['routes']:
        source_route=next(v for v in original['generationContract']['routes']if v['id']==r['id'])
        r['steps']=copy.deepcopy(source_route['steps'])
        r['localDisplacementBlocks']=[(z-a)/128 for a,z in zip(ports[r['from']]['position'],ports[r['to']]['position'])]
    for v in g['validations']:v.update(result='UNKNOWN',artifacts=[],method='pending_exact_macro_core_revalidation')
    receipt=dict(schema='pcg/macro-original-core-repair/v1',source=reference,
        originalNinePlatformRectanglesExact=all(c['platforms'][:9]==s['platforms']for c,s in zip(cases,original_cases)),
        originalProgramsExact=all(c['control_plan']==s['control_plan']for c,s in zip(cases,original_cases)),
        originalDoorsAndRewardsExact=all(c['latches']==s['latches']and c['reward_sites']==s['reward_sites']for c,s in zip(cases,original_cases)),
        addedDocks=dock_data,maximumSourceBrakeX=lip+105,firstAddedRightDockX=928,
        sourceBNormal=source_ports['B']['normal'],newBNormal=[1,0],
        reason='Independent small boundary landing zones; do not move core shores or bridge the brake fall.',
        maximumRevisions=2,validation='UNKNOWN',humanReview='UNKNOWN')
    g['generation']['migration']['corePreservingMacroRepair']=receipt
    doc,cases,bindings=bind(doc,cases)
    from .causal_observer_v2 import bind as bind_observer
    doc,cases,observer_bindings=bind_observer(doc,cases)
    corners.annotate(doc)
    out.mkdir(parents=True)
    doc,children=persist_macro_components(source,out,doc)
    core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases))
    meta=core.read(prepared/'migration.json')
    for key in('physicsReport','boundaryProbe','godotLoad'):meta.pop(key,None)
    meta.update(status='prepared_unverified',internalGeometryChanged=True,evidence=[],corePreservingMacroRepair=receipt,
                specificEpisodeObservers=observer_bindings)
    core.write(out/'migration.json',meta);core.write(out/'component-receipts.json',children)
    core.write(out/'macro-core-repair.json',receipt);core.write(out/'boundary-bindings.json',bindings)
    core.write(out/'specific-observer-bindings.json',observer_bindings)
    core.contract(out/'module.mapnote.json',refresh=True)
    return dict(status='prepared_unverified',folder=str(out),receipt=receipt)


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source-prefix',required=True);p.add_argument('--out',required=True);args=p.parse_args()
    print(json.dumps(prepare(args.source_prefix,args.out),ensure_ascii=False))
