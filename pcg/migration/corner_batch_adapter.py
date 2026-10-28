"""Offline four-corner data adaptation; real certification remains with Harness.

Only a body-width window in the selected corner Block becomes a one-way dock.
All remaining rock fragments retain their collision/material coverage. The old
side receives no added wall and is no longer a declared Port for this config.
"""
from __future__ import annotations
import copy
import re
import subprocess
from pathlib import Path
from . import core, corners

SCHEMA = 'pcg/corner-interface-adaptation/v2'
POLICY = 'preserve_geometry_no_extra_closure'


class AdaptationGap(ValueError):
    """A concrete data-binding gap, never evidence of physical impossibility."""


def configuration_id(port_id, corner):
    token = re.sub('[^a-z0-9_-]+', '-', str(port_id).lower()).strip('-')
    if not token or corner not in corners.CORNERS:
        raise AdaptationGap('invalid_corner_selection')
    return f'{token}-{corner.lower().replace("_", "-")}-open-v2'


def _rect(obj):
    return [obj[k] for k in ('x', 'y', 'w', 'h')]


def _intersection(a, b):
    x, y = max(a[0], b[0]), max(a[1], b[1])
    right, bottom = min(a[0]+a[2], b[0]+b[2]), min(a[1]+a[3], b[1]+b[3])
    return [x, y, right-x, bottom-y] if right > x+1e-7 and bottom > y+1e-7 else None


def _subtract(rect, window):
    cut = _intersection(rect, window)
    if cut is None:
        return [list(rect)]
    x,y,w,h = rect; a,b,c,d = cut
    pieces = [[x,y,w,b-y], [x,b+d,w,y+h-b-d], [x,b,a-x,d], [a+c,b,x+w-a-c,d]]
    return [r for r in pieces if r[2] > 1e-7 and r[3] > 1e-7]


def _same(a,b):
    return len(a)==len(b) and all(abs(x-y)<1e-7 for x,y in zip(a,b))


def _stands(rect, position):
    return rect[0]+12-1e-6 <= position[0] <= rect[0]+rect[2]-12+1e-6 and abs(position[1]+18-rect[1]) < 1e-5


def adapt_data(document, input_cases, port_id, corner):
    """Pure geometric/program binding. Returned candidate is wholly UNVERIFIED."""
    doc, cases = copy.deepcopy(document), copy.deepcopy(input_cases)
    if not cases:
        raise AdaptationGap('corner_requires_frozen_route_cases')
    gc = doc['generationContract']; base_version = gc['contentVersion']
    port = next((p for p in gc['ports'] if p['id']==port_id), None)
    if port is None:
        raise AdaptationGap('unknown_corner_port:'+str(port_id))
    option = corners.options(doc, port).get(corner)
    if not option or not option['applicable']:
        raise AdaptationGap('port_is_not_on_requested_corner')
    if port['face'] not in ('LEFT','RIGHT') or option['targetFace'] not in ('TOP','BOTTOM'):
        raise AdaptationGap('current_batch_requires_side_to_vertical_corner')
    objects = {o['id']:o for o in doc['objects']}
    host = objects.get(port.get('support',{}).get('objectId'))
    if not host or host['type'] not in ('terrain','platform') or host.get('trackId') or host.get('rotation',0):
        raise AdaptationGap('corner_requires_axis_aligned_static_support')
    original_port = copy.deepcopy(port); original_objects = copy.deepcopy(doc['objects'])
    bounds = gc['space']['bounds']; block = gc['foundation']['blockSize']
    tx,ty = option['targetPosition']; corner_y = bounds['y'] if corner.startswith('TOP') else bounds['y']+bounds['h']-block
    # Forty-eight pixels preserve the original side's full 24px body support:
    # the side staging is 24px from its edge; the new center is 64px away.
    window = [tx-24,host['y'],48,corner_y+block-host['y']]
    if window[3] <= 0 or host['y'] < corner_y or window[0] < bounds['x'] or window[0]+48 > bounds['x']+bounds['w']:
        raise AdaptationGap('original_support_top_outside_corner_block')
    dock_rect = list(window)
    count = len(cases[0]['platforms'])
    if any(len(c['platforms']) != count for c in cases):
        raise AdaptationGap('route_platform_counts_differ')
    edited=[]; added=[]; next_index=count
    # Co-planar or contained duplicate floor rectangles must also become
    # passable in this same local window, or they silently block down-through.
    for obj in doc['objects']:
        if obj['type']!='terrain' or obj.get('trackId') or not _intersection(_rect(obj),window):
            continue
        index=obj.get('sourceIndex')
        if obj.get('rotation',0) or not isinstance(index,int) or any(index>=len(c['platforms']) or not _same(c['platforms'][index],_rect(obj)) for c in cases):
            raise AdaptationGap('corner_static_geometry_binding_missing:'+obj['id'])
        if any(o.get('hostId')==obj['id'] for o in doc['objects']) or any(t.get('platform_index')==index for c in cases for t in c.get('thorns',[])):
            raise AdaptationGap('corner_window_intersects_attached_cell_host:'+obj['id'])
        before=_rect(obj); pieces=_subtract(before,window)
        if pieces:
            # Prefer the fragment supporting an unselected original Port.
            stations=[p.get('stagingPosition') for p in gc['ports'] if p['id']!=port_id and p.get('support',{}).get('objectId')==obj['id']]
            pieces.sort(key=lambda r:(sum(_stands(r,s) for s in stations if s),r[2]*r[3]),reverse=True)
            first=pieces[0]
        else:
            # Retain dense platform/source indices without a zero-area ghost.
            # This pre-existing small collider becomes a one-way fragment.
            first=_intersection(before,window); obj['type']='platform';obj['wallClimbable']=False
        for key,value in zip(('x','y','w','h'),first):obj[key]=value
        for number,rect in enumerate(pieces[1:],1):
            fragment=copy.deepcopy(obj);fragment.update(id=obj['id']+'/corner-rem-'+str(number),sourceIndex=next_index)
            next_index+=1
            for key,value in zip(('x','y','w','h'),rect):fragment[key]=value
            added.append(fragment)
        edited.append(dict(objectId=obj['id'],sourceIndex=index,before=before,after=first,remainingSolidRectangles=pieces))
    dock=copy.deepcopy(host)
    dock.update(id=doc['id']+'/corner-'+port_id+'-'+corner.lower()+'-dock',type='platform',sourceIndex=next_index,wallClimbable=False)
    for key,value in zip(('x','y','w','h'),dock_rect):dock[key]=value
    added.append(dock);doc['objects']+=added
    # Existing optional movement links are not copied onto the short dock.
    for key in ('trackId','trackPosition','sourceId','mechanics'):
        dock.pop(key,None)
    lookup={o['id']:o for o in doc['objects']}
    normal=[0,-1 if option['targetFace']=='TOP' else 1]
    port.update(position=list(option['targetPosition']),normal=normal,face=option['targetFace'],surface='ONE_WAY_PLATFORM',
                stagingPosition=[tx,dock['y']-18],support=dict(objectId=dock['id'],face='top',status='source_derived'),
                crossing_offset=[0,dock['y']-18-ty])
    aperture=[tx-24,ty-32,48,64]
    if isinstance(port.get('connection'),dict):
        port['connection']['region']=dict(zip(('x','y','w','h'),aperture))
    if isinstance(port.get('grid'),dict):port['grid']['stagingPosition']=list(port['stagingPosition'])
    marker=lookup[port['objectId']];marker.update(x=tx-marker['w']/2,y=ty-marker['h']/2)
    support_rebindings=[]
    for p in gc['ports']:
        if p['id']==port_id:continue
        previous=p.get('support',{})
        if not isinstance(previous,dict) or p.get('surface')=='AIR':continue
        old_host=objects.get(previous.get('objectId'))
        if old_host is None or not any(e['objectId']==old_host['id']for e in edited):continue
        kind='terrain'if p['surface']=='ROCK'else'platform';position=p['stagingPosition']
        candidates=[o for o in doc['objects'] if o['type']==kind and not o.get('trackId') and _stands(_rect(o),position)]
        if not candidates:raise AdaptationGap('unselected_port_loses_body_support:'+p['id'])
        target=min(candidates,key=lambda o:(o['id']!=previous['objectId'],abs(o['sourceIndex']-old_host['sourceIndex'])))
        p['support']={**previous,'objectId':target['id']}
        if target['id']!=previous['objectId']:support_rebindings.append(dict(portId=p['id'],fromObjectId=previous['objectId'],toObjectId=target['id']))
    for case in cases:
        platforms=case['platforms'];oneway=set(case.get('one_way_platform_indices',[]));walls=set(case.get('wall_platform_indices',[]))
        for obj in doc['objects']:
            if obj['type']not in('terrain','platform') or obj.get('trackId'):continue
            i=obj['sourceIndex'];rect=_rect(obj)
            if i<len(platforms):platforms[i]=rect
            elif i==len(platforms):platforms.append(rect)
            else:raise AdaptationGap('non_dense_corner_platform_mapping')
            if obj['type']=='platform':oneway.add(i);walls.discard(i)
            elif obj.get('wallClimbable'):walls.add(i)
        case['one_way_platform_indices']=sorted(oneway);case['wall_platform_indices']=sorted(walls)
        for p in gc['ports']:
            cp=next((v for v in case['ports']if v['id']==p['id']),None)
            if cp is None:raise AdaptationGap('route_lacks_declared_port:'+p['id'])
            if p['id']==port_id:cp.update(position=list(p['stagingPosition']),normal=list(normal))
            if isinstance(p.get('support'),dict):cp['support_index']=lookup[p['support']['objectId']]['sourceIndex']
        bp=case['block_ports'][port_id]
        bp.update(position=list(port['position']),normal=list(normal),stagingPosition=list(port['stagingPosition']),aperture=list(aperture),crossing_offset=list(port['crossing_offset']))
        if isinstance(bp.get('grid'),dict):
            bp['grid'].update(edge='N'if normal[1]<0 else'S',stagingPosition=list(port['stagingPosition']))
        # The original runner wrappers read this per-case table dynamically;
        # absent entries retain the existing Harness's vertical controls.
        case.get('migration_boundary_plans',{}).pop(port_id,None)
        case.pop('recorded_frames',None)
    for route in gc['routes']:
        a=next(p for p in gc['ports']if p['id']==route['from']);z=next(p for p in gc['ports']if p['id']==route['to'])
        route['localDisplacementBlocks']=[(b-a)/block for a,b in zip(a['position'],z['position'])]
    for v in gc['validations']:
        v.update(result='UNKNOWN',artifacts=[],failures=[],method='pending_actual_corner_open_configuration',coverage={},unverified=['corner configuration physics not yet run'])
    for obj in added:
        gc['space']['occupancy']['objectIds'].append(obj['id'])
        gc['composition']['cells'].append(dict(id=obj['id'],objectIds=[obj['id']],contentVersion='sha256:'+'0'*64))
    corners.annotate(doc)
    config=configuration_id(port_id,corner)
    gc['generation']['cornerConfiguration']=dict(id=config,baseContentVersion=base_version,retiredSidePolicy=POLICY,meaning='Same logical Port moved to adjacent corner face; no added side closure')
    adaptation=dict(schema=SCHEMA,configurationId=config,selectedPortId=port_id,corner=corner,retiredSidePolicy=POLICY,
        cornerBlock=dict(x=tx-block/2,y=corner_y,w=block,h=block),conversionWindow=dict(zip(('x','y','w','h'),window)),
        originalPort=original_port,targetPort=copy.deepcopy(port),originalSupport=_rect(next(o for o in original_objects if o['id']==original_port['support']['objectId'])),
        edits=edited,addedObjects=[dict(id=o['id'],type=o['type'],sourceIndex=o['sourceIndex'],rect=_rect(o))for o in added],
        supportRebindings=support_rebindings,oldOpeningClosure=None,canonicalProgramsChanged=False,
        selectedBoundaryPlansRetired=True,abilityAndResourceRequirementsChanged=False,geometryCertification='NOT_RUN')
    return doc,cases,adaptation


def prepare(source, out, port_id, corner):
    source,out=Path(source).resolve(),Path(out).resolve()
    if out.is_relative_to(core.ACTIVE)or out.is_relative_to(core.RECYCLE):raise ValueError('prepare_corner_outside_authoritative_archives_first')
    if out.exists():raise ValueError('corner_batch_destination_exists')
    original=core.read(source/'module.mapnote.json');inputs=source/'physics-input-cases.json'
    if not inputs.exists():inputs=source/'cases.json'
    doc,cases,adaptation=adapt_data(original,core.read(inputs)['cases'],port_id,corner)
    base_sha=core.sha(source/'module.mapnote.json');input_sha=core.sha(inputs);config=adaptation['configurationId']
    doc['generationContract']['generation']['cornerConfiguration']['basePhysicsInputSha256']=input_sha
    out.mkdir(parents=True);core.write(out/'module.mapnote.json',doc);core.write(out/'cases.json',dict(cases=cases))
    meta=core.read(source/'migration.json')
    for key in ('physicsReport','godotLoad','boundaryProbe','holdoutPool','diagnosticsReconciliationHistory'):meta.pop(key,None)
    meta.update(status='prepared_unverified',evidence=[],internalGeometryChanged=True,unresolved=['corner-open configuration awaits real physical validation'],
        cornerConfiguration=dict(id=config,portId=port_id,corner=corner,baseContentVersion=original['generationContract']['contentVersion'],
            baseDocumentSha256=base_sha,basePhysicsInputSha256=input_sha,source=core.relative(source),
            originalPort=adaptation['originalPort'],retiredSidePolicy=POLICY))
    core.write(out/'migration.json',meta)
    script="""import fs from 'node:fs';import {canonical,sha256} from './module-contract.js';const p=process.argv[1],d=JSON.parse(fs.readFileSync(p));for(const c of d.generationContract.composition.cells){const os=c.objectIds.map(id=>d.objects.find(o=>o.id===id));c.contentVersion='sha256:'+sha256(canonical(os.length===1?os[0]:os));}fs.writeFileSync(p,JSON.stringify(d,null,2)+'\\n');"""
    subprocess.run(['node','--input-type=module','-e',script,str(out/'module.mapnote.json')],cwd=core.REPO,check=True)
    core.contract(out/'module.mapnote.json',refresh=True)
    adaptation.update(baseDocumentSha256=base_sha,targetDocumentSha256=core.sha(out/'module.mapnote.json'),source=core.relative(source))
    core.write(out/'corner-adaptation.json',adaptation)
    protocol=core.read(core.STATE/'protocol-full-v2.json')
    core.write(out/'corner-protocol.json',dict(schema='pcg/corner-interface-experiment-protocol/v2',configurationId=config,
        retiredSidePolicy=POLICY,baseModuleSource=core.relative(source),frozenTargetDocumentSha256=core.sha(out/'module.mapnote.json'),
        fixedGeometry=True,maximumAttempts=350,calibrationSeed=protocol['calibrationSeed'],holdoutSeed=protocol['holdoutSeed'],
        trialsPerNoiseLevel=12,thresholds=dict(clean=.9,mild=.85,moderate=.65),
        selection='One predeclared local open-side adaptation; no holdout reselection',
        required=['all original directed route programs','all original permissions','complete-body vertical ingress and egress',
                  'continuous route exit without reset','actual compiled playable package'],
        unknown=['arbitrary external state','unsearched route pairs','full Map','human review']))
    return dict(status='prepared_unverified',folder=str(out),configurationId=config,retiredSidePolicy=POLICY)
