"""Deterministic, inspectable Block/shore adaptation of existing real geometry.

This module edits data only. It never labels a route or interface as certified;
all changed colliders and programs must go through the existing Godot Harness.
The original inputs remain untouched, and no physics approximation is used.
"""
from __future__ import annotations
import copy
import math
from collections import Counter
from pathlib import Path

BLOCK = 128
FACE = {(-1, 0): 'LEFT', (1, 0): 'RIGHT', (0, -1): 'TOP', (0, 1): 'BOTTOM'}
NON_GEOMETRY = {'entry', 'exit', 'route', 'anchor', 'note'}


def _rect(obj):
    return [float(obj[k]) for k in ('x', 'y', 'w', 'h')]


def _same(a, b):
    return len(a) == len(b) and all(abs(x-y) < .001 for x, y in zip(a, b))


def _support_index(port, case, objects):
    found = next((p.get('support_index') for p in case.get('ports', [])
                  if p['id'] == port['id']), None)
    if found is not None:
        return found
    reference = port.get('support', {})
    host = objects.get(reference.get('objectId')) if isinstance(reference, dict) else None
    if host:
        return next((i for i, rect in enumerate(case['platforms']) if _same(rect, _rect(host))), None)
    return None


def _extent(doc, cases):
    rects = [_rect(o) for o in doc['objects'] if o['type'] not in NON_GEOMETRY
             and all(isinstance(o.get(k), (int, float)) for k in ('x', 'y', 'w', 'h'))]
    # Include actual body trajectories reserved by the original author, not the
    # old camera/death-zone world_bounds or unbounded projectile flight space.
    rects += [[r[k] for k in ('x', 'y', 'w', 'h')]
              for r in doc['generationContract']['space'].get('actionClearance', {}).get('regions', [])
              if isinstance(r, dict) and all(k in r for k in ('x', 'y', 'w', 'h'))]
    for case in cases:
        rects += case['platforms']
        for platform in case.get('moving_platforms', []):
            for key in ('start', 'finish'):
                if key in platform:
                    x, y = platform[key]; w, h = platform['size']
                    # The real mover stores center positions, not top-left.
                    rects.append([x-w/2, y-h/2, w, h])
    for envelope in doc['generationContract']['space'].get('dynamicEnvelopes', []):
        region = envelope.get('region')
        if isinstance(region, dict):
            rects.append([region[k] for k in ('x','y','w','h')])
    if not rects:
        raise ValueError('adaptation_no_actual_geometry')
    return [min(r[0] for r in rects), min(r[1] for r in rects),
            max(r[0]+r[2] for r in rects), max(r[1]+r[3] for r in rects)]


def _append_platform(doc, cases, identifier, rect, one_way=False):
    obj = dict(id=identifier, type='platform' if one_way else 'terrain',
               x=rect[0], y=rect[1], w=rect[2], h=rect[3], rotation=0,
               label='Local boundary connector', note='Offline adaptation; physics pending')
    doc['objects'].append(obj)
    occupancy = doc['generationContract']['space'].get('occupancy', {})
    occupancy.setdefault('objectIds', []).append(identifier)
    index = len(cases[0]['platforms'])
    obj['sourceIndex'] = index
    for case in cases:
        if len(case['platforms']) != index:
            raise ValueError('route_geometries_have_different_platform_counts')
        case['platforms'].append(list(rect))
        if one_way:
            case.setdefault('one_way_platform_indices', []).append(index)
    return obj, index


def _move_docked_points(case, old, new):
    """Only move real standing endpoints/rewards on the changed shore.

    A direction, size, aim vector, cooldown, or historical author parameter is
    deliberately never interpreted as a point by a generic recursive walker.
    """
    delta = new[1]-old[1]
    if not delta:
        return
    def standing(point):
        return (isinstance(point, list) and len(point) >= 2 and
                old[0]-1 <= point[0] <= old[0]+old[2]+1 and abs(point[1]-(old[1]-18)) < 3)
    for key in ('spawn', 'entry_port', 'exit_port'):
        if standing(case.get(key)):
            case[key][1] += delta
    goal = case.get('goal')
    if goal and old[0]-1 <= goal[0]+goal[2]/2 <= old[0]+old[2]+1 and abs(goal[1]+goal[3]/2-(old[1]-18)) < 12:
        goal[1] += delta
    for reward in case.get('reward_sites', []):
        if standing(reward.get('position')):
            reward['position'][1] += delta
            if isinstance(reward.get('region'), list):
                reward['region'][1] += delta
    for enemy in case.get('enemies', []):
        if standing(enemy.get('position')):
            enemy['position'][1] += delta


def adapt(document, input_cases):
    """Return (document, cases, receipt); never mutate the supplied originals.

    Rectangle origin may be non-zero. Choosing its vertical phase is equivalent
    to translating the local coordinate frame, and avoids changing most shores.
    A failed engine replay is a repair result, never automatic admission.
    """
    doc, cases = copy.deepcopy(document), copy.deepcopy(input_cases)
    if not cases:
        raise ValueError('adaptation_requires_real_cases')
    gc = doc['generationContract']; objects = {o['id']: o for o in doc['objects']}
    old_bounds = copy.deepcopy(gc['space']['bounds'])
    old_platforms = copy.deepcopy(cases[0]['platforms'])
    supports = {}
    for port in gc['ports']:
        index = _support_index(port, cases[0], objects)
        if index is None:
            raise ValueError('actual_port_support_not_identified:'+port['id'])
        supports[port['id']] = index
    # Most horizontal ports share one shore phase. Choose the most frequent
    # phase, then closest old origin, so their colliders remain vertically exact.
    phases = Counter(round((old_platforms[supports[p['id']]][1]-96) % BLOCK, 5)
                     for p in gc['ports'] if p['normal'][0])
    phase = min(phases, key=lambda p: (-phases[p], abs((p-old_bounds['y']+64) % BLOCK-64))) if phases else old_bounds['y'] % BLOCK
    xmin, ymin, xmax, ymax = _extent(doc, cases)
    bx = math.floor(xmin/BLOCK)*BLOCK
    by = phase + math.floor((ymin-phase)/BLOCK)*BLOCK
    w = max(BLOCK, math.ceil((xmax-bx)/BLOCK)*BLOCK)
    h = max(BLOCK, math.ceil((ymax-by)/BLOCK)*BLOCK)
    bounds = dict(x=bx, y=by, w=w, h=h)
    edits, port_edits, changed_indices = [], [], {}
    extension_requests = []
    connector_supports = {}
    for port in gc['ports']:
        if not port['normal'][0]:
            continue
        index = supports[port['id']]
        old = old_platforms[index]
        if index not in changed_indices:
            # floor = Block center +32; player center is floor-18. The 14px
            # difference between port anchor and body staging is intentional.
            desired = by+96+round((old[1]-by-96)/BLOCK)*BLOCK
            changed_indices[index] = [old[0], desired, old[2], max(8, old[1]+old[3]-desired)]
        new = changed_indices[index]
        side = port['normal'][0]
        extension = old[0]-bx if side<0 else bx+w-old[0]-old[2]
        if extension>.001:
            extension_requests.append((port,index,extension))
    for index, new in changed_indices.items():
        old = old_platforms[index]
        for case in cases:
            if not _same(case['platforms'][index], old):
                raise ValueError('route_geometry_disagrees_at_shore:'+str(index))
            _move_docked_points(case, old, new)
            # start_offset is measured from the platform's local left edge.
            # Preserve a hosted thorn's original world location after extension.
            for thorn in case.get('thorns', []):
                if thorn.get('platform_index') == index:
                    if thorn.get('face') in ('top','bottom'):
                        thorn['start_offset'] += old[0]-new[0]
                    else:
                        thorn['start_offset'] += old[1]-new[1]
            case['platforms'][index] = list(new)
        hosts = [o for o in doc['objects'] if o['type'] in ('terrain', 'platform') and _same(_rect(o), old)]
        if len(hosts) != 1:
            raise ValueError('editable_shore_geometry_ambiguous:'+str(index))
        host = hosts[0]
        for k, v in zip(('x', 'y', 'w', 'h'), new):host[k] = v
        if not _same(old, new):
            edits.append(dict(kind='endpoint_shore', platformIndex=index, objectId=host['id'],
                              before=old, after=new, topDelta=new[1]-old[1],
                              leftExtension=old[0]-new[0], rightExtension=new[0]+new[2]-old[0]-old[2]))
        for obj in doc['objects']:
            if obj.get('hostId') == host['id'] and obj['type'] in ('spike','wallSpike'):
                source = next((t for t in cases[0].get('thorns',[]) if t.get('surface_id')==obj.get('sourceId')), None)
                if source and source.get('face') == 'top':obj['y'] += new[1]-old[1]
        # Editor reward rectangles follow the actual shifted runtime reward.
        dy = new[1]-old[1]
        if dy:
            for obj in doc['objects']:
                if obj['type'] == 'reward' and old[0] <= obj['x']+obj['w']/2 <= old[0]+old[2] and abs(obj['y']+obj['h']/2-(old[1]-18)) < 40:
                    obj['y'] += dy
                    source = obj.get('mechanics', {}).get('source')
                    if isinstance(source,dict):
                        actual = next((r for r in cases[0].get('reward_sites',[]) if r['id']==source.get('id')),None)
                        if actual:obj['mechanics']['source'] = copy.deepcopy(actual)
    for endpoint,index,length in extension_requests:
        source = cases[0]['platforms'][index]
        side = endpoint['normal'][0]
        overlap = min(24, source[2])
        rect = ([bx,source[1],source[0]-bx+overlap,min(24,source[3])] if side<0 else
                [source[0]+source[2]-overlap,source[1],bx+w-source[0]-source[2]+overlap,min(24,source[3])])
        one_way = index in cases[0].get('one_way_platform_indices',[])
        obj,new_index = _append_platform(doc,cases,f"{endpoint['objectId'].rsplit('/',1)[0]}/migration-shore-{endpoint['id']}",rect,one_way)
        connector_supports[endpoint['id']] = (obj,new_index)
        edits.append(dict(kind='boundary_connector',portId=endpoint['id'],sourcePlatformIndex=index,
            platformIndex=new_index,objectId=obj['id'],rect=rect,length=length,thickness=rect[3],
            preservesOriginalBankSpan=True,validation='UNKNOWN'))
    # End caps authored just beyond an old endpoint are not the challenge's
    # gates. Cut only the new outward body corridor, preserving all unrelated
    # terrain, typed gate Cells, and hazard-hosted terrain.
    protected = set(supports.values()) | {t['platform_index'] for c in cases for t in c.get('thorns',[]) if 'platform_index' in t}
    for endpoint,source_index,length in extension_requests:
        bank = cases[0]['platforms'][source_index]
        side = endpoint['normal'][0]
        left,right = (bx,bank[0]) if side<0 else (bank[0]+bank[2],bx+w)
        floor = bank[1]
        if right-left<.01:continue
        corridor = [left,floor-48,right-left,48]
        for index,rect in list(enumerate(cases[0]['platforms'])):
            if index in protected or index>=len(old_platforms):continue
            # Wide floors and roofs stay intact. The adapter only opens narrow
            # non-mechanism end caps in the newly added outward approach.
            if rect[2]>64 or rect[3]<64:continue
            x0=max(rect[0],corridor[0]);x1=min(rect[0]+rect[2],corridor[0]+corridor[2])
            y0=max(rect[1],corridor[1]);y1=min(rect[1]+rect[3],floor)
            if x1-x0<.01 or y1-y0<.01:continue
            host=next((o for o in doc['objects']if o['type']=='terrain'and _same(_rect(o),rect)),None)
            if host is None:continue
            if any(o.get('hostId')==host['id']for o in doc['objects']):continue
            pieces=[]
            if y0>rect[1]:pieces.append([rect[0],rect[1],rect[2],y0-rect[1]])
            if y1<rect[1]+rect[3]:pieces.append([rect[0],y1,rect[2],rect[1]+rect[3]-y1])
            if x0>rect[0]:pieces.append([rect[0],y0,x0-rect[0],y1-y0])
            if x1<rect[0]+rect[2]:pieces.append([x1,y0,rect[0]+rect[2]-x1,y1-y0])
            if not pieces:raise ValueError('whole_endcap_removal_requires_explicit_binding:'+str(index))
            for case in cases:
                case['platforms'][index]=list(pieces[0])
            for key,value in zip(('x','y','w','h'),pieces[0]):host[key]=value
            extra=[]
            for piece_no,piece in enumerate(pieces[1:]):
                obj,new_index=_append_platform(doc,cases,host['id']+'-corridor-'+str(piece_no),piece)
                extra.append(dict(objectId=obj['id'],platformIndex=new_index,rect=piece))
            edits.append(dict(kind='outward_endcap_body_window',portId=endpoint['id'],
                platformIndex=index,objectId=host['id'],before=rect,after=pieces[0],
                removedRegion=[x0,y0,x1-x0,y1-y0],additionalPieces=extra,
                scope='Only new outward corridor; no gates or hazard hosts modified',validation='UNKNOWN'))
    # Thin original shores can need a lower canonical floor. Expand the
    # rectangle after actual edits rather than leaving their colliders outside.
    actual_min = min(o['y'] for o in doc['objects'] if o['type'] not in NON_GEOMETRY)
    actual_max = max(o['y']+o['h'] for o in doc['objects'] if o['type'] not in NON_GEOMETRY)
    by = min(by, phase+math.floor((actual_min-phase)/BLOCK)*BLOCK)
    h = max(h, math.ceil((actual_max-by)/BLOCK)*BLOCK)
    bounds.update(y=by,h=h)
    for port in gc['ports']:
        old = dict(position=copy.deepcopy(port['position']),
                   stagingPosition=copy.deepcopy(port.get('grid', {}).get('stagingPosition', port['position'])))
        index = supports[port['id']]
        if port['id'] in connector_supports:
            connector_obj,index = connector_supports[port['id']]
            port['support'] = dict(objectId=connector_obj['id'],face='top',status='source_derived')
        support = cases[0]['platforms'][index]
        nx, ny = port['normal']; connector = []
        if nx:
            anchor = [bx if nx < 0 else bx+w, support[1]-32]
            staging = [anchor[0]-nx*24, support[1]-18]
        else:
            # A former internal TOP marker needs real one-way landing geometry,
            # not a ROCK marker moved upward. Small staggered decks preserve the
            # original endpoint and let the real jump/recoil mechanism ascend.
            center = bx+(min(int(w/BLOCK)-1,max(0,round((old['stagingPosition'][0]-bx-64)/BLOCK)))+.5)*BLOCK
            anchor = [center, by if ny < 0 else by+h]
            if ny > 0:
                raise ValueError('bottom_port_requires_authored_vertical_connector:'+port['id'])
            original_top = support[1]
            terminal_top = by+32
            step_count = max(1, math.ceil((original_top-terminal_top)/80))
            for step in range(step_count):
                top = original_top-(original_top-terminal_top)*(step+1)/step_count
                offset = 0 if step == step_count-1 else (-20 if step%2 else 20)
                rect = [center+offset-48, top, 96, 12]
                obj, index = _append_platform(doc, cases, f"{port['objectId'].rsplit('/',1)[0]}/migration-{port['id']}-step-{step}", rect, True)
                connector.append(dict(objectId=obj['id'], platformIndex=index, rect=rect))
            support = cases[0]['platforms'][index]
            port['support'] = dict(objectId=connector[-1]['objectId'], face='top', status='source_derived')
            staging = [center, support[1]-18]
            edits.append(dict(kind='vertical_one_way_connector', portId=port['id'], platforms=connector))
        port['position'] = anchor
        port['grid'] = dict(stagingPosition=staging)
        marker = objects.get(port.get('objectId'))
        if marker:
            marker['x'], marker['y'] = anchor[0]-marker['w']/2, anchor[1]-marker['h']/2
        surface = 'ONE_WAY_PLATFORM' if index in cases[0].get('one_way_platform_indices', []) else 'ROCK'
        if nx:
            aperture = [anchor[0]-32,anchor[1]-32,64,64]
        else:
            aperture = [anchor[0]-32,anchor[1]-32,64,64]
        for case in cases:
            ports = case.setdefault('ports', [])
            runtime_port = next((p for p in ports if p['id']==port['id']), None)
            if runtime_port is None:
                runtime_port = dict(id=port['id']); ports.append(runtime_port)
            runtime_port.update(position=staging,normal=copy.deepcopy(port['normal']),support_index=index)
            case.setdefault('block_ports', {})[port['id']] = dict(id=port['id'],position=anchor,
                normal=copy.deepcopy(port['normal']),stagingPosition=staging,aperture=aperture,
                crossing_offset=[staging[0]-anchor[0],staging[1]-anchor[1]])
        port_edits.append(dict(portId=port['id'], before=old,
            after=dict(position=anchor,stagingPosition=staging,supportIndex=index,surface=surface),
            connectorPlatforms=connector, routeContinuationRequired=bool(connector)))
    # Bind editor enemy bodies to their real adapted runtime spawn, not a stale
    # preview center. Enemy timing and behavior fields remain untouched.
    for obj in doc['objects']:
        if obj['type']=='enemy':
            actual=next((e for e in cases[0].get('enemies',[])if e['id']==obj.get('sourceId')),None)
            if actual:
                obj['x']=actual['position'][0]-obj['w']/2
                obj['y']=actual['position'][1]-obj['h']/2
        if obj['type'] in ('terrain','platform') and not obj.get('trackId'):
            declared_index=obj.get('sourceIndex')
            index=(declared_index if isinstance(declared_index,int) and declared_index<len(cases[0]['platforms']) and _same(_rect(obj),cases[0]['platforms'][declared_index]) else
                   next((i for i,p in enumerate(cases[0]['platforms'])if _same(_rect(obj),p)),None))
            if index is not None:
                if gc['kind']=='macro' and obj.get('sourceIndex')!=index:
                    obj['migrationOriginalSourceIndex']=obj.get('sourceIndex')
                obj['sourceIndex']=index
    gc['space']['bounds'] = bounds
    # Previous polyomino reservation rectangles describe obsolete ownership.
    # Real object refs and actual body/envelope reservations remain authoritative.
    gc['space'].get('occupancy', {})['regions'] = []
    for seam in gc['space'].get('seams', []):
        endpoint = next(p for p in gc['ports'] if p['id']==seam['portId'])
        x,y = endpoint['position']; seam['region'] = dict(x=x-32,y=y-32,w=64,h=64)
        seam['status'] = 'UNKNOWN'
    gc['space'].pop('blockGrid', None)
    gc['space']['boundsCoverage'] = 'Complete rectangle computed from real Cells and original body action reservations; shore adaptation pending real physics.'
    # Keep kill/recovery bounds permissive for real experiments, independent of
    # Module ownership. Runtime bodies/projectiles may cross a declared Port.
    for case in cases:
        case.pop('recorded_frames', None)
        case.pop('factory_evidence', None)
        case.pop('module_sha256', None)
        case.pop('block_grid', None)
        original_world = case.get('world_bounds',[bounds['x'],bounds['y'],bounds['w'],bounds['h']])
        left=min(original_world[0],bounds['x']-128);top=min(original_world[1],bounds['y']-128)
        right=max(original_world[0]+original_world[2],bounds['x']+bounds['w']+128)
        bottom=max(original_world[1]+original_world[3],bounds['y']+bounds['h']+128)
        case['world_bounds']=[left,top,right-left,bottom-top]
        case['migration_adaptation'] = dict(rectangle=bounds, portAdaptations=port_edits,
            changedShoreIndices=sorted(changed_indices), validation='UNKNOWN')
    receipt = dict(schema='pcg/module-geometry-adaptation/v1', translation=[0,0],
        frameOriginPhase=phase, beforeBounds=old_bounds, afterBounds=bounds,
        internalGeometryChanged=bool(edits), edits=edits, portAdaptations=port_edits,
        status='adapted_unverified', missingPhysicsClaims=['entry from new boundary through original core',
            'continuous exit', 'cheap bypass counterexamples', 'recovery and declared return'])
    return doc, cases, receipt



def component_documents(document, source_documents):
    """Rebind real Macro children, keeping internal contacts distinct from exports.

    Internal component interfaces need not be the parent's outer interfaces.
    A former contact such as gate.C is therefore retained, and its new external
    shore is exported as C-external. Parent route steps explicitly use derived
    child routes for their changed first/last legs. Children remain v1 internal
    definitions, not independently certified rectangular library Modules.
    """
    gc = document['generationContract']
    if gc['kind'] != 'macro':return {}
    result = {part['id']:copy.deepcopy(source_documents[part['id']])
              for part in gc['composition']['components']}
    exports = {}
    for export in gc['composition']['exports']:
        instance = export['source']['instanceId']; old_id=export['source']['portId']
        child=result[instance]; cg=child['generationContract']; prefix=instance+'/'
        old=next(p for p in cg['ports'] if p['id']==old_id)
        parent=next(p for p in gc['ports']if p['id']==export['portId'])
        marker=next(o for o in document['objects']if o['id']==parent['objectId'])
        external_marker=copy.deepcopy(marker);external_marker['id']=prefix+old['objectId']+'-external'
        document['objects'].append(external_marker)
        original_marker=next(o for o in child['objects']if o['id']==old['objectId'])
        restored=copy.deepcopy(original_marker);restored['id']=prefix+original_marker['id']
        for key in ('trackId','targetId','hostId'):
            if key in restored:restored[key]=prefix+restored[key]
        marker.clear();marker.update(restored)
        parent['objectId']=external_marker['id']
        external=copy.deepcopy(old); external['id']=old_id+'-external'
        external['position']=copy.deepcopy(parent['position'])
        external['stagingPosition']=copy.deepcopy(parent.get('stagingPosition',parent.get('grid',{}).get('stagingPosition',parent['position'])))
        external['objectId']=external_marker['id'][len(prefix):]
        external['normal']=copy.deepcopy(parent['normal'])
        external['support']=copy.deepcopy(parent['support'])
        if isinstance(external['support'],dict):
            external['support']['objectId']=external['support']['objectId'].removeprefix(prefix)
        external['seamIds']=[external['id']+'-seam']
        cg['space']['seams'].append(dict(id=external['seamIds'][0],portId=external['id'],
            region='UNKNOWN',status='UNKNOWN',allowedOverlap=[]))
        cg['ports'].append(external)
        export['source']['portId']=external['id']
        exports[export['portId']]=(instance,external['id'],old_id)
    for route in gc['routes']:
        # A source Route may begin at an internal link (e.g. gate.C ->
        # brake.D). Add its new external-to-contact leg explicitly.
        for entry in (True,False):
            step = route['steps'][0 if entry else -1]
            if step['kind']!='connection':continue
            instance,external_id,internal_id=exports[route['from']if entry else route['to']]
            cg=result[instance]['generationContract']
            derived=copy.deepcopy(cg['routes'][0]);derived['id']='migration-'+route['id']+('-entry'if entry else'-exit')
            derived['from'],derived['to']=(external_id,internal_id)if entry else(internal_id,external_id)
            derived['validationIds']=[];derived['availability']='UNKNOWN';derived['return']=dict(status='UNKNOWN',conditions='UNKNOWN')
            cg['routes'].append(derived)
            additional=dict(kind='component_route',instanceId=instance,routeId=derived['id'])
            if entry:route['steps'].insert(0,additional)
            else:route['steps'].append(additional)
        component_steps=[(i,step)for i,step in enumerate(route['steps'])if step['kind']=='component_route']
        for ordinal,(position,step) in enumerate(component_steps):
            child=result[step['instanceId']];cg=child['generationContract']
            original=next(r for r in cg['routes']if r['id']==step['routeId'])
            derived=copy.deepcopy(original);derived['id']='migration-'+route['id']+'-'+str(position)
            if ordinal==0:
                instance,port,_=exports[route['from']]
                if instance!=step['instanceId']:raise ValueError('macro_first_component_mismatch')
                derived['from']=port
            if ordinal==len(component_steps)-1:
                instance,port,_=exports[route['to']]
                if instance!=step['instanceId']:raise ValueError('macro_last_component_mismatch')
                derived['to']=port
            derived['validationIds']=[];derived['availability']='UNKNOWN'
            derived['return']=dict(status='UNKNOWN',conditions='UNKNOWN')
            cg['routes'].append(derived);step['routeId']=derived['id']
    for part in gc['composition']['components']:
        child=result[part['id']];cg=child['generationContract'];prefix=part['id']+'/'
        if part['transform']['translation']!=[0,0] or part['transform'].get('mirrorX')or part['transform']['rotation']:
            raise ValueError('macro_component_transform_requires_explicit_rebind:'+part['id'])
        def local(value):return value.removeprefix(prefix)if isinstance(value,str)else value
        old_objects={o['id']:o for o in child['objects']}; actual=[]
        for obj in document['objects']:
            if not obj['id'].startswith(prefix):continue
            new=copy.deepcopy(obj)
            for key in ('id','trackId','targetId','hostId'):
                if key in new:new[key]=local(new[key])
            actual.append(new)
        child['objects']=actual
        actual_by_id={o['id']:o for o in actual}
        for port in cg['ports']:
            support=actual_by_id.get(port.get('support',{}).get('objectId')) if isinstance(port.get('support'),dict) else None
            if support and port['support'].get('face')=='top' and port['id'] in {p['id']for p in source_documents[part['id']]['generationContract']['ports']}:
                port['stagingPosition']=[port['position'][0],support['y']-18]
        cg['space']['bounds']=copy.deepcopy(gc['space']['bounds'])
        cg['space']['occupancy']['objectIds']=[o['id']for o in actual if o['type']not in NON_GEOMETRY]
        cg['space']['occupancy']['regions']=[]
        for o in actual:
            if o['id']not in old_objects and o['type']not in NON_GEOMETRY:
                cg['composition']['cells'].append(dict(id='migration-'+str(len(cg['composition']['cells'])),
                    contentVersion='sha256:'+'0'*64,objectIds=[o['id']]))
        cg['relations']=[dict(from_=a['id'],to=b['id'],status='UNKNOWN',conditions='UNKNOWN',
            routeIds=[r['id']for r in cg['routes']if r['from']==a['id']and r['to']==b['id']])
            for a in cg['ports']for b in cg['ports']if a['id']!=b['id']]
        for rel in cg['relations']:rel['from']=rel.pop('from_')
        cg['generation']['componentMigration']=dict(sourceContentVersion=source_documents[part['id']]['generationContract']['contentVersion'],
            parentModuleId=document['id'],componentInstanceId=part['id'],validation='UNKNOWN',
            scope='Internal component definition; parent Macro separately verified; no child physics certificate inherited.')
        for validation in cg['validations']:
            validation.update(result='UNKNOWN',artifacts=[],method='pending_parent_macro_revalidation')
    return result


def persist_macro_components(original_folder, prepared_folder, document=None):
    """Persist rebound children, return the updated parent and bound receipts."""
    from pathlib import Path
    from . import core
    original_folder=Path(original_folder);prepared_folder=Path(prepared_folder)
    document=copy.deepcopy(document if document is not None else core.read(prepared_folder/'module.mapnote.json'))
    gc=document['generationContract']
    if gc['kind']!='macro':return document,[]
    record=core.read(original_folder/'record.json');sources={};receipts=[]
    for part in gc['composition']['components']:
        reference=next((a for a in record['evidence']if a['path'].endswith('/'+part['moduleId']+'.mapnote.json')),None)
        if reference is None:raise ValueError('original_macro_component_not_in_source_receipt:'+part['id'])
        core.verify_artifacts([reference]);source=core.read(core.resolve_artifact(reference['path']))
        if source['generationContract']['contentVersion']!=part['contentVersion']:
            raise ValueError('macro_source_component_version_changed:'+part['id'])
        sources[part['id']]=source
    children=component_documents(document,sources)
    for part in gc['composition']['components']:
        target=prepared_folder/'components'/part['id']/'module.mapnote.json'
        core.write(target,children[part['id']]);core.contract(target,refresh=True)
        rebound=core.read(target);old_version=part['contentVersion']
        part['contentVersion']=rebound['generationContract']['contentVersion']
        part['definitionPath']=str(target.relative_to(prepared_folder))
        receipts.append(dict(instanceId=part['id'],sourceVersion=old_version,
            contentVersion=part['contentVersion'],path=part['definitionPath'],sha256=core.sha(target),
            scope='Rebound internal component; parent Macro physics required'))
    return document,receipts


def bind_internal_waypoints(document, input_cases, original_cases):
    """Separate authored grounded core visits from newly exported boundary Ports.

    Call only for the explicitly supported original local-dock validators. Route
    endpoint Ports retain their new outer positions and real crossing tests.
    Each old visit survives as a named, grounded, real-trace waypoint assertion.
    """
    from .physics import author_for
    from .migration_purpose import _AUTHORS
    from . import core
    doc,cases=copy.deepcopy(document),copy.deepcopy(input_cases)
    gc=doc['generationContract'];declared={p['id']:p for p in gc.get('internalWaypoints',[])}
    receipts=[]
    for case,original in zip(cases,original_cases):
        via=original.get('route_spec',{}).get('via_ports',[])
        if not via:continue
        if case['id']!=original['id']:raise ValueError('waypoint_source_case_order_changed')
        author=author_for(original);source=Path(author.__file__).resolve().relative_to(core.REPO).as_posix()
        if source not in _AUTHORS:raise ValueError('waypoint_author_not_explicitly_supported:'+source)
        points=[]
        for pid in via:
            if pid in (original['route_spec']['from_port'],original['route_spec']['to_port']):
                raise ValueError('external_via_endpoint_requires_actual_boundary_visit:'+pid)
            port=next(p for p in original['ports']if p['id']==pid)
            index=port.get('support_index')
            if index is None:raise ValueError('internal_waypoint_source_support_missing:'+pid)
            delta=case['platforms'][index][1]-original['platforms'][index][1]
            position=[port['position'][0],port['position'][1]+delta]
            identifier='core-waypoint-'+pid
            point=dict(id=identifier,objectId=doc['id']+'/migration-'+identifier,sourcePortId=pid,
                position=position,originalPosition=copy.deepcopy(port['position']),
                requiredGrounded=True,interpretation='original_grounded_internal_dock',validation='UNKNOWN')
            if identifier in declared and declared[identifier]['position']!=position:
                raise ValueError('same_internal_waypoint_has_different_geometry:'+pid)
            if identifier not in declared:
                declared[identifier]=point
                doc['objects'].append(dict(id=point['objectId'],type='anchor',x=position[0]-12,y=position[1]-18,w=24,h=36,
                    rotation=0,label='Core dock '+pid,note='Preserved authored grounded waypoint; separate from outer Port '+pid))
            points.append(copy.deepcopy(point))
        case['route_spec']['source_via_ports']=copy.deepcopy(via)
        case['route_spec']['via_ports']=[]
        case['route_spec']['via_waypoints']=[p['id']for p in points]
        case['migration_purpose']=dict(schema='pcg/internal-waypoint-purpose-binding/v1',
            originalAuthorSource=source,waypoints=points,
            policy='Keep original real grounded dock checks; outer entry and exit remain independent actual Port tests.')
        case.setdefault('generation_rule',{})['migrationOriginalRegistrationSource']=source
        case['generation_rule']['registration_source']='pcg/migration/migration_purpose.py'
        route_id=case['route_spec']['id']
        route=next(r for r in gc['routes']if r['id']==route_id)
        route['viaWaypoints']=[p['id']for p in points]
        for program in gc.get('generation',{}).get('parameters',{}).get('routePrograms',[]):
            if program['routeId']==route_id:
                program['sourceViaPorts']=copy.deepcopy(program.get('viaPorts',via))
                program['viaPorts']=[];program['viaWaypoints']=route['viaWaypoints']
        receipts.append(dict(caseId=case['id'],routeId=route_id,originalAuthorSource=source,
            sourceViaPorts=copy.deepcopy(via),internalWaypoints=points,externalPortsUnchanged=True))
    gc['internalWaypoints']=list(declared.values())
    return doc,cases,dict(schema='pcg/internal-waypoint-migration/v1',rows=receipts,
        validation='UNKNOWN',certificateInherited=False)
