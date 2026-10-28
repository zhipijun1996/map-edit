"""Offline corner-Port assessments; no geometry or physics certification by fiat.

Existing current documents are assessed into a separate version-bound inventory.
New prepared documents can call ``annotate`` before their content version freezes.
Only a separately executed, complete Port configuration may grant permission.
"""
from __future__ import annotations

import math
import copy

CORNERS = ('TOP_LEFT', 'TOP_RIGHT', 'BOTTOM_LEFT', 'BOTTOM_RIGHT')
NORMALS = {'LEFT': [-1, 0], 'RIGHT': [1, 0], 'TOP': [0, -1], 'BOTTOM': [0, 1]}


def options(document, port):
    """Return four explicit corner attributes, including non-applicable corners.

    A 1x1 Module may have two applicable alternatives for one Port. Coordinates
    are relative to the actual rectangle origin, which may be negative.
    """
    c = document['generationContract']
    b = c['space']['bounds']
    size = c.get('foundation', {}).get('blockSize', 128)
    width, height = b['w'] / size, b['h'] / size
    x, y = port['position']
    face = port.get('face') or next((f for f, n in NORMALS.items() if n == port.get('normal')), None)
    output = {}
    for corner in CORNERS:
        left, top = corner.endswith('LEFT'), corner.startswith('TOP')
        faces = ('LEFT' if left else 'RIGHT', 'TOP' if top else 'BOTTOM')
        bx, by = (0 if left else width - 1), (0 if top else height - 1)
        source = {
            'LEFT': [b['x'], b['y'] + (by + .5) * size],
            'RIGHT': [b['x'] + b['w'], b['y'] + (by + .5) * size],
            'TOP': [b['x'] + (bx + .5) * size, b['y']],
            'BOTTOM': [b['x'] + (bx + .5) * size, b['y'] + b['h']],
        }
        applicable = (width >= 1 and height >= 1 and width.is_integer() and height.is_integer()
                      and face in faces and all(math.isclose(a, z, rel_tol=0, abs_tol=1e-5)
                                                for a, z in zip((x, y), source[face])))
        row = dict(applicable=applicable, allowed='UNKNOWN' if applicable else False,
                   reason='local_interface_adaptation_and_real_physics_required' if applicable
                          else 'port_not_on_this_corner_block_outer_face', profileId=None)
        if applicable:
            target = faces[1] if face == faces[0] else faces[0]
            surface = port.get('surface', 'UNKNOWN')
            if surface == 'ROCK' and target in ('TOP', 'BOTTOM'):
                surface = 'ONE_WAY_PLATFORM'
                row['reason'] = 'rock_vertical_forbidden_requires_local_one_way_platform_adaptation'
            if surface == 'AIR' and target == 'BOTTOM' and port.get('permission') != 'OUTPUT':
                surface = 'ONE_WAY_PLATFORM'
                row['reason'] = 'bottom_air_input_forbidden_requires_local_one_way_platform_adaptation'
            row.update(targetFace=target, targetPosition=source[target],
                       proposedSurface=surface, permission=port.get('permission', 'UNKNOWN'))
        output[corner] = row
    return output


def annotate(document):
    """Add unverified assessments in-place; caller must rebind contentVersion.

    Never preserve pre-existing ``allowed: true`` after an adaptation. Profiles
    must be re-certified against the resulting content and configuration bytes.
    """
    c = document['generationContract']
    for port in c['ports']:
        port['cornerRelocations'] = options(document, port)
    c['portConfigurations'] = []
    return document


def assess_document(document):
    c = document['generationContract']
    ports = [dict(portId=p['id'], sourceFace=p.get('face'), sourcePosition=p['position'],
                  cornerRelocations=options(document, p)) for p in c['ports']]
    return dict(schema='pcg/corner-port-assessment/v1', contentVersion=c['contentVersion'],
                moduleDocumentId=document['id'], ports=ports,
                applicableOptions=sum(o['applicable'] for p in ports for o in p['cornerRelocations'].values()),
                certifiedOptions=0, physics='NOT_RUN',
                meaning='Assessment only. UNKNOWN is unavailable to Map matching.')


def audit_inventory(root=None):
    """Assess all current, pending generated, and prepared migration documents.

    This separate receipt deliberately leaves certified current bytes unchanged.
    Source originals are assessed as found, never relabelled as standard ports.
    """
    from . import core
    root = root or core.REPO
    rows = []
    seen = set()
    locations = [('current', root / 'modules'),
                 ('pending_generated', core.LEGACY),
                 ('prepared', root / '.cache/migration')]
    for scope, folder in locations:
        documents=folder.rglob('module.mapnote.json') if scope=='prepared' else folder.glob('*/module.mapnote.json')
        for path in sorted(documents):
            relative = path.relative_to(root).as_posix()
            if relative in seen:
                continue
            seen.add(relative)
            doc = core.read(path)
            if 'generationContract' not in doc:
                continue
            row = assess_document(doc)
            row.update(source=relative, documentSha256=core.sha(path), scope=scope)
            if scope=='current':
                receipts=verified_receipts(path.parent.name,row['documentSha256'],row['contentVersion'])
                for artifact in receipts:
                    receipt=core.read(core.REPO/artifact['path'])
                    for selection in receipt['relocations']:
                        item=next(p for p in row['ports']if p['portId']==selection['portId'])
                        option=item['cornerRelocations'][selection['corner']]
                        option.update(allowed=True,profileId=receipt['configurationId'],
                                      reason='actual_configuration_physics_and_native_package_reverified',
                                      receipt=artifact)
                row['certifiedOptions']=sum(o['allowed']is True for p in row['ports']for o in p['cornerRelocations'].values())
                if receipts:row['physics']='VERIFIED_FOR_EXACT_CONFIGURATIONS'
            rows.append(row)
    report = dict(schema='pcg/corner-port-inventory/v1', rows=rows,
                  counts={scope: sum(r['scope'] == scope for r in rows) for scope, _ in locations},
                  applicableOptions=sum(r['applicableOptions'] for r in rows),
                  certifiedOptions=sum(r['certifiedOptions']for r in rows),
                  physics='See individual configuration evidence; UNKNOWN assessments grant no rights.')
    core.write(core.STATE / 'corner-port-inventory-v1.json', report)
    return report


OPEN_RECEIPT_SCHEMA = 'pcg/corner-port-configuration/v2'
OPEN_RETIRED_SIDE_POLICY = 'preserve_geometry_no_extra_closure'


def verify_open_geometry(base, target, relocations):
    """Check local material/occupancy changes, without simulating any physics.

    Splitting existing rocks may add objects but may not add solid coverage.
    Only a short target dock and its downward slice may become one-way. Actual
    body passage, routes and resource semantics remain real Harness obligations.
    """
    b = base['generationContract']['space']['bounds']
    size = base['generationContract']['foundation']['blockSize']
    before = {o['id']: o for o in base['objects']}
    after = {o['id']: o for o in target['objects']}
    windows = []; markers = set()
    for relocation in relocations:
        port = next(p for p in base['generationContract']['ports'] if p['id'] == relocation['portId'])
        corner = relocation['corner']; option = options(base, port)[corner]
        host = before.get(port.get('support', {}).get('objectId'))
        if not host or host['type'] not in ('terrain', 'platform') or host.get('trackId'):
            raise ValueError('corner_open_static_source_support_required')
        left = b['x'] if corner.endswith('LEFT') else b['x'] + b['w'] - size
        top = b['y'] if corner.startswith('TOP') else b['y'] + b['h'] - size
        tx = option['targetPosition'][0]
        # 64px is a bound on local support adaptation, not an invented bridge.
        # The current adapter uses 48px so a body has tolerance at a narrow bank.
        windows.append((max(left, tx-32), max(top, host['y']), min(left+size, tx+32), top+size))
        markers.add(port['objectId'])
    def static(o):
        return o['type'] in ('terrain', 'platform') and not o.get('trackId')
    # Preserve all mechanisms, rewards, route drawings and unselected markers.
    old_other = {k:v for k,v in before.items() if not static(v)}
    new_other = {k:v for k,v in after.items() if not static(v)}
    if set(old_other) != set(new_other): raise ValueError('corner_open_nonterrain_object_set_changed')
    for key, original in old_other.items():
        changed = new_other[key]
        if key in markers:
            original = {k:v for k,v in original.items() if k not in ('x','y')}
            changed = {k:v for k,v in changed.items() if k not in ('x','y')}
        if original != changed: raise ValueError('corner_open_nonterrain_object_changed:'+key)
    old_rects = [o for o in before.values() if static(o)]
    new_rects = [o for o in after.values() if static(o)]
    for o in old_rects + new_rects:
        if o.get('rotation', 0) != 0 or o['w'] <= 0 or o['h'] <= 0:
            raise ValueError('corner_open_axis_aligned_positive_static_rectangles_required')
    xs = sorted({v for o in old_rects+new_rects for v in (o['x'],o['x']+o['w'])}
                | {v for w in windows for v in (w[0],w[2])})
    ys = sorted({v for o in old_rects+new_rects for v in (o['y'],o['y']+o['h'])}
                | {v for w in windows for v in (w[1],w[3])})
    xi = {v:i for i,v in enumerate(xs)}; yi = {v:i for i,v in enumerate(ys)}
    def raster(rects):
        cells = {}
        for o in rects:
            tag = (o['type'], bool(o.get('wallClimbable',False)))
            for x in range(xi[o['x']], xi[o['x']+o['w']]):
                for y in range(yi[o['y']], yi[o['y']+o['h']]):
                    cells.setdefault((x,y), set()).add(tag)
        return cells
    a, z = raster(old_rects), raster(new_rects)
    changed_cells = 0
    for cell in a.keys() | z.keys():
        old, new = a.get(cell,set()), z.get(cell,set())
        if old == new: continue
        x,y = cell; px=(xs[x]+xs[x+1])/2; py=(ys[y]+ys[y+1])/2
        if not any(l <= px <= r and t <= py <= bottom for l,t,r,bottom in windows):
            raise ValueError('corner_open_geometry_change_outside_local_target_dock')
        if any(kind=='terrain' for kind,wall in new-old):
            raise ValueError('corner_open_added_solid_closure_or_collision')
        if any(kind=='platform' and wall for kind,wall in new-old):
            raise ValueError('corner_open_added_wall_climb_surface')
        changed_cells += 1
    return dict(passed=True, changedPartitionCells=changed_cells,
                retiredSidePolicy=OPEN_RETIRED_SIDE_POLICY,
                scope='Exact local static occupancy/material difference only; not physics or Map certification.')


def _verify_open_adaptation(base_folder, folder, base, target, receipt):
    from . import core
    if receipt.get('retiredSidePolicy') != OPEN_RETIRED_SIDE_POLICY:
        raise ValueError('corner_open_retired_side_policy_required')
    if 'retiredOpeningReport' in receipt:
        raise ValueError('corner_open_receipt_cannot_relabel_legacy_closed_policy')
    proof = receipt.get('adaptation')
    if not isinstance(proof, dict) or not proof.get('path') or not proof.get('sha256'):
        raise ValueError('corner_open_actual_adaptation_artifact_required')
    path = core.resolve_artifact(proof['path'])
    if path.resolve() != (folder/'corner-adaptation.json').resolve():
        raise ValueError('corner_open_adaptation_artifact_path_changed')
    core.verify_artifacts([proof]); report = core.read(path)
    expected = dict(schema='pcg/corner-interface-adaptation/v2',
        retiredSidePolicy=OPEN_RETIRED_SIDE_POLICY,
        baseDocumentSha256=core.sha(base_folder/'module.mapnote.json'),
        targetDocumentSha256=core.sha(folder/'module.mapnote.json'))
    if any(report.get(key) != value for key,value in expected.items()):
        raise ValueError('corner_open_adaptation_not_bound_to_actual_documents')
    if len(receipt['relocations']) == 1:
        selection = receipt['relocations'][0]
        if report.get('selectedPortId') != selection['portId'] or report.get('corner') != selection['corner']:
            raise ValueError('corner_open_adaptation_selection_mismatch')
    verify_open_geometry(base, target, receipt['relocations'])


def verified_receipts(module_id, document_sha256, content_version):
    """Return only independently rederived, current external configurations.

    These receipts are outside the base document's semantic hash, so certifying
    an alternative does not invalidate the already frozen base Module. No
    ``allowed`` or ``technicalStatus`` input is sufficient without real raw
    physics, exact compiled geometry and actual native playback receipts.
    """
    from . import core, physics
    from .godot_package import verify_package
    base_folder = core.ACTIVE / core.safe_id(module_id)
    base_path = base_folder / 'module.mapnote.json'
    if not base_path.is_file() or core.sha(base_path) != document_sha256:
        raise ValueError('corner_receipt_base_bytes_changed')
    base = core.read(base_path)
    if base['generationContract']['contentVersion'] != content_version:
        raise ValueError('corner_receipt_base_version_changed')
    result = []
    for path in sorted((base_folder/'port-configurations').glob('*/receipt.json')):
        receipt = core.read(path)
        if receipt.get('baseContentVersion') != content_version or receipt.get('baseDocumentSha256') != document_sha256:
            # Old configuration evidence remains on disk but grants no rights
            # to an edited base. It is not a reason to reject the base itself.
            continue
        if receipt.get('schema') not in ('pcg/corner-port-configuration/v1', OPEN_RECEIPT_SCHEMA) or receipt.get('moduleId') != module_id:
            raise ValueError('corner_configuration_receipt_identity_mismatch')
        if receipt.get('allowed') is not True or receipt.get('technicalStatus') != 'verified':
            continue
        base_inputs=base_folder/'physics-input-cases.json'
        if not base_inputs.exists():base_inputs=base_folder/'cases.json'
        if not base_inputs.is_file()or core.sha(base_inputs)!=receipt.get('basePhysicsInputSha256'):
            raise ValueError('corner_configuration_base_programs_changed')
        folder = path.parent
        for field, name in (('configuration','module.mapnote.json'), ('package','godot-package.json')):
            artifact = receipt.get(field, {})
            target = core.REPO / artifact.get('path', '')
            if target.resolve() != (folder/name).resolve() or not target.is_file() or core.sha(target) != artifact.get('sha256'):
                raise ValueError('corner_configuration_artifact_changed:'+field)
        target_doc = core.read(folder/'module.mapnote.json')
        gc = target_doc['generationContract']
        if gc['contentVersion'] != receipt['configuration']['contentVersion'] or target_doc['id'] != base['id']:
            raise ValueError('corner_configuration_bound_to_other_template')
        for key in ('capabilityRequirements','difficulty'):
            if target_doc.get(key) != base.get(key):
                raise ValueError('corner_configuration_changes_'+key)
        base_gc=base['generationContract']
        if gc.get('requiredNativeProfile')!=base_gc.get('requiredNativeProfile') or gc.get('generation',{}).get('parameters',{}).get('original_tuning_profile')!=base_gc.get('generation',{}).get('parameters',{}).get('original_tuning_profile'):
            raise ValueError('corner_configuration_changes_native_ability_resource_profile')
        base_ports = {p['id']:p for p in base['generationContract']['ports']}
        target_ports = {p['id']:p for p in gc['ports']}
        if set(base_ports) != set(target_ports):
            raise ValueError('corner_configuration_changes_logical_ports')
        selected = set()
        relocations = receipt.get('relocations', [])
        if not relocations:raise ValueError('corner_configuration_missing_selection')
        for relocation in relocations:
            pid, corner = relocation['portId'], relocation['corner']
            if pid in selected or pid not in base_ports or corner not in CORNERS:
                raise ValueError('corner_configuration_invalid_selection')
            selected.add(pid)
            option = options(base, base_ports[pid])[corner]
            p = target_ports[pid]
            if not option['applicable'] or p['face'] != option['targetFace'] or p['position'] != option['targetPosition']:
                raise ValueError('corner_configuration_target_not_nearest_same_block_face')
            if p['permission'] != base_ports[pid]['permission']:
                raise ValueError('corner_configuration_changes_initial_permission')
            if any(relocation.get(k) != p[key] for k,key in
                   [('targetFace','face'),('targetPosition','position'),('surface','surface'),('permission','permission')]):
                raise ValueError('corner_receipt_does_not_describe_actual_port')
        for pid in set(base_ports)-selected:
            for key in ('position','normal','face','surface','permission'):
                if target_ports[pid][key] != base_ports[pid][key]:
                    raise ValueError('corner_configuration_changes_unselected_port')
        def signatures(doc):
            return sorted((r['id'],r['from'],r['to'],tuple(r['requiredAbilities'])) for r in doc['generationContract']['routes'])
        if signatures(target_doc) != signatures(base):
            raise ValueError('corner_configuration_discards_or_changes_original_route_requirements')
        if gc['space']['bounds'] != base['generationContract']['space']['bounds'] or gc['foundation'] != base['generationContract']['foundation']:
            raise ValueError('corner_configuration_changes_module_footprint')
        if not core.contract(folder/'module.mapnote.json')['versionMatches']:
            raise ValueError('corner_configuration_stale_content_version')
        physics.verify_report(folder,receipt['physicsReport'])
        if receipt['schema'] == OPEN_RECEIPT_SCHEMA:
            _verify_open_adaptation(base_folder, folder, base, target_doc, receipt)
        else:
            from .corner_experiment import verify_closed
            verify_closed(folder,receipt['retiredOpeningReport'])
        verify_package(folder,require_loaded=True)
        result.append(dict(path=core.relative(path),sha256=core.sha(path)))
    return result


if __name__ == '__main__':
    import json
    report = audit_inventory()
    print(json.dumps({k: v for k, v in report.items() if k != 'rows'}, ensure_ascii=False))


def compiled_ports(document, verified_references):
    """Consumer view: measured permissions overlay immutable source proposals.

    A true option names an entire precompiled configuration. It never licenses
    rotating only the marker or combining independently certified alternatives.
    """
    from . import core
    ports=[]
    for port in document['generationContract']['ports']:
        value={k:copy.deepcopy(port[k])for k in ('id','position','face','surface','permission','initialPermissionConditions')if k in port}
        value['cornerRelocations']=options(document,port)
        ports.append(value)
    by_id={p['id']:p for p in ports}
    for reference in verified_references:
        core.verify_artifacts([reference])
        receipt=core.read(core.resolve_artifact(reference['path']))
        for selected in receipt['relocations']:
            option=by_id[selected['portId']]['cornerRelocations'][selected['corner']]
            if not option['applicable']or option['targetFace']!=selected['targetFace']or option['targetPosition']!=selected['targetPosition']:
                raise ValueError('certified_corner_selection_no_longer_matches_base')
            option.update(allowed=True,profileId=receipt['configurationId'],
                proposedSurface=selected['surface'],reason='actual_offline_certified_whole_configuration')
            identities=option.setdefault('configurationIds',[])
            if receipt['configurationId']not in identities:identities.append(receipt['configurationId'])
    return ports
