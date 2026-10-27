"""Single-current archive operations, using existing sketches and evidence.

No original is removed until a prepared module has passed validation and been
read back. The journal is also the relocation map for immutable old evidence.
"""
from __future__ import annotations
import copy
import contextlib
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ACTIVE = REPO / 'modules'
RECYCLE = REPO / 'modules-recycle'
STATE = REPO / 'pcg/migration/foundation-v1'
LEGACY = REPO / 'pcg/map_directed/library/candidates'
JOURNAL = STATE / 'ledger.json'
_CATALOG_DEFERRED = 0


@contextlib.contextmanager
def batch_enrollment():
    """Keep relocation WALs per item; rebuild the persistent index once."""
    global _CATALOG_DEFERRED
    _CATALOG_DEFERRED += 1
    try:
        yield
    finally:
        _CATALOG_DEFERRED -= 1
        if not _CATALOG_DEFERRED:
            build_catalog()


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n'
    with tempfile.NamedTemporaryFile(mode='w', dir=path.parent, delete=False) as stream:
        stream.write(data)
        temporary = Path(stream.name)
    temporary.replace(path)


def relative(path):
    return Path(path).resolve().relative_to(REPO).as_posix()


def original_package_path(folder):
    """Only direct inventoried source packages, never shared game/runtime assets."""
    folder = Path(folder).resolve()
    return folder.parent == LEGACY.resolve() or folder.parent == (REPO/'pcg/migration/game-sources').resolve()


def safe_id(value):
    if not re.fullmatch(r'[a-z0-9][a-z0-9_-]{0,139}', value):
        raise ValueError('unsafe_module_id')
    return value


def ledger():
    return read(JOURNAL) if JOURNAL.exists() else dict(
        schema='pcg/module-migration-ledger/v1', foundationVersion='1.0',
        entries={}, relocations={})


def resolve_artifact(path, journal=None):
    # Resolve archived bytes without rewriting the historical document/hash.
    journal = journal or ledger()
    source = (REPO / path).resolve()
    if not source.is_relative_to(REPO):
        raise ValueError('artifact_outside_repository')
    if source.is_file():
        return source
    for before, after in sorted(journal['relocations'].items(), key=lambda item: -len(item[0])):
        if path == before or path.startswith(before + '/'):
            target = (REPO / (after + path[len(before):])).resolve()
            if not target.is_relative_to(RECYCLE):
                raise ValueError('invalid_relocation')
            return target
    return source


def verify_artifacts(items, journal=None):
    missing = []
    for item in items:
        path = resolve_artifact(item['path'], journal)
        if not path.is_file() or sha(path) != item['sha256']:
            missing.append(item['path'])
    if missing:
        raise ValueError('missing_or_changed_evidence:' + ','.join(missing[:8]))


def contract(document, refresh=False):
    standards = read(STATE/'standards-source.json')
    for source in standards['sources']:
        if sha(REPO/source['repository_path']) != source['sha256']:
            raise ValueError('foundation_source_changed_rebind_standard_before_migration:'+source['repository_path'])
    command = ['node', str(REPO / 'pcg/migration/document.mjs'),
               str(Path(document).resolve())]
    if refresh:
        command.append('--refresh')
    result = subprocess.run(command, cwd=REPO, capture_output=True, text=True)
    if result.returncode:
        raise ValueError(result.stderr.strip() or result.stdout.strip())
    return json.loads(result.stdout)


def legacy_cases(folder):
    if (folder / 'cases.json').exists():
        value = read(folder / 'cases.json')
        return value['cases'] if isinstance(value, dict) else value
    return [read(folder / 'case.json')]


def assess(folder):
    folder = Path(folder)
    doc = read(folder / 'module.mapnote.json')
    gc = doc['generationContract']
    bounds = gc['space']['bounds']
    size = 128
    gaps = []
    if bounds['w'] % size or bounds['h'] % size:
        gaps.append('size_not_block_multiple')
    invalid_ports = []
    for port in gc['ports']:
        x, y = port['position']; nx, ny = port['normal']
        bx, by, w, h = [bounds[key] for key in ('x', 'y', 'w', 'h')]
        edge = ((nx == -1 and abs(x-bx) < 1e-5) or
                (nx == 1 and abs(x-bx-w) < 1e-5) or
                (ny == -1 and abs(y-by) < 1e-5) or
                (ny == 1 and abs(y-by-h) < 1e-5))
        midpoint = abs(((y-by if nx else x-bx) % size)-size/2) < 1e-5
        if not edge or not midpoint:
            invalid_ports.append(port['id'])
    if invalid_ports:
        gaps.append('ports_need_real_boundary_adaptation:' + ','.join(invalid_ports))
    record = read(folder / 'record.json')
    if record.get('document_sha256') != sha(folder/'module.mapnote.json') or record.get('contentVersion') != gc['contentVersion']:
        gaps.append('legacy_document_identity_or_bytes_changed')
    case_file = folder/('cases.json' if (folder/'cases.json').exists() else 'case.json')
    expected_cases = record.get('cases_sha256',record.get('case_sha256'))
    if not expected_cases or expected_cases != sha(case_file):
        gaps.append('legacy_case_bytes_changed')
    if not record.get('technical_status', '').startswith('passed') and not (record.get('sourceType') == 'original_game' and folder.parent.resolve() == (REPO/'pcg/migration/game-sources').resolve()):
        gaps.append('legacy_technical_status_not_passed')
    if gc['kind'] != 'module':
        gaps.append('macro_requires_component_migration')
    try:
        verify_artifacts([artifact for validation in gc.get('validations', [])
                          for artifact in validation['artifacts']])
    except ValueError as error:
        gaps.append(str(error))
    return dict(source=relative(folder), contentVersion=gc['contentVersion'],
                title=doc['title'], kind=gc['kind'], bounds=bounds,
                portCount=len(gc['ports']), legacyTechnicalStatus=record.get('technical_status'),
                migrationStatus='needs_verification' if not gaps else 'needs_repair',
                gaps=gaps, humanReview='UNKNOWN', destination='original')


def audit():
    journal = ledger()
    rows = []
    withdrawn = set()
    for file in (REPO / 'pcg/feedback/content-withdrawals').glob('*.json'):
        withdrawn.update(read(file).get('contentVersions', []))
    holds = {}
    view = REPO / 'generation/workshop/plains-recoil-current/catalog.json'
    if view.exists():
        holds = {r['contentVersion']: r.get('selection_reason') for r in read(view)['rows']}
    for file in sorted(LEGACY.glob('*/record.json')):
        row = assess(file.parent)
        if row['contentVersion'] in withdrawn:
            row['migrationStatus'] = 'withdrawn_review'
            row['gaps'].append('technical_withdrawal_preserved')
        if holds.get(row['contentVersion']) == 'pacing_held':
            row['migrationStatus'] = 'human_design_hold'
            row['gaps'].append('human_design_hold_preserved')
        previous = journal['entries'].get(row['source'], {})
        if previous.get('migrationStatus') in ('active', 'recycled'):
            raise ValueError('archived_source_reappeared:' + row['source'])
        journal['entries'][row['source']] = {**previous, **row}
        rows.append(row)
    write(JOURNAL, journal)
    return dict(schema='pcg/module-migration-audit/v1', inspected=len(rows),
                counts={status: sum(row['migrationStatus'] == status for row in rows)
                        for status in sorted({r['migrationStatus'] for r in rows})}, rows=rows)


def prepare(folder, out, module_id=None):
    folder = Path(folder).resolve(); out = Path(out).resolve()
    if not original_package_path(folder):
        raise ValueError('prepare_requires_unmigrated_original_package')
    report = assess(folder)
    repairable = ('size_not_block_multiple', 'ports_need_real_boundary_adaptation:', 'macro_requires_component_migration')
    blocking = [gap for gap in report['gaps'] if not any(gap.startswith(code) for code in repairable)]
    if blocking:
        return dict(status='needs_repair', conflicts=blocking,
                    searched=['unaltered_internal_geometry', 'existing_rectangle_and_ports'],
                    negotiable=['real_port_shore_adaptation', 'separate_internal_redesign'],
                    source=report['source'])
    journal = ledger()
    review_status = journal['entries'].get(report['source'], {}).get('migrationStatus')
    if review_status == 'withdrawn_review':
        raise ValueError('technical_withdrawal_requires_repair_before_admission')
    if out.exists():
        raise ValueError('prepared_destination_exists')
    if out.is_relative_to(ACTIVE) or out.is_relative_to(RECYCLE):
        raise ValueError('prepare_outside_archive_first')
    doc = read(folder / 'module.mapnote.json')
    cases = legacy_cases(folder)
    for index, case in enumerate(cases):
        if not case.get('route_spec'):
            route = doc['generationContract']['routes'][min(index, len(doc['generationContract']['routes'])-1)]
            case['route_spec'] = dict(id=route['id'], from_port=route['from'], to_port=route['to'], role=route['role'])
    original_cases = copy.deepcopy(cases)
    old_version = doc['generationContract']['contentVersion']
    adaptation = dict(internalGeometryChanged=False, translation=[0, 0], edits=[])
    if any(gap.startswith(('size_not_block_multiple', 'ports_need_real_boundary_adaptation:')) for gap in report['gaps']):
        from .adaptation import adapt
        doc, cases, adaptation = adapt(doc, cases)
    gc = doc['generationContract']
    specification = read(folder / 'record.json').get('specification', {})
    module_id = safe_id(module_id or re.sub(r'[^a-z0-9_-]+', '-',
                         specification.get('id', doc['id']).lower()).strip('-')[:140])
    bounds = gc['space']['bounds']; size = 128
    gc['version'] = 2
    gc['foundation'] = dict(version='1.0', blockSize=size,
                            widthBlocks=int(bounds['w']/size), heightBlocks=int(bounds['h']/size))
    gc['space'].pop('blockGrid', None)
    gc['space']['boundsCoverage'] = 'Complete rectangular Module footprint; internal geometry preserved.'
    gc['legacyCertification'] = dict(contentVersion=old_version,
                                    scope='Historical witness only; not a v2 certificate.')
    old_validations = {v['routeId']: v for v in gc.get('validations', []) if v['kind'] == 'physics'}
    gc['validations'] = []
    gc['closures'] = []
    gc['mirror'] = dict(status='UNKNOWN', validationIds=[])
    for port in gc['ports']:
        grid = port.pop('grid', {})
        port['stagingPosition'] = grid.get('stagingPosition', port['position'])
        port['face'] = {(-1, 0): 'LEFT', (1, 0): 'RIGHT', (0, -1): 'TOP', (0, 1): 'BOTTOM'}[tuple(port['normal'])]
        support = next((o for o in doc['objects'] if o['id'] == port.get('support', {}).get('objectId')), None) if isinstance(port.get('support'), dict) else None
        if support is None:
            raise ValueError('surface_requires_real_support_assessment:' + port['id'])
        port['surface'] = 'ONE_WAY_PLATFORM' if support['type'] == 'platform' else 'ROCK'
        # Local bidirectional boundary traversal must be measured separately;
        # this declaration alone grants no route or composition admission.
        port['permission'] = port.get('permission', 'INOUT')
        port['permissionStatus'] = 'declared_pending_boundary_probe'
    gc['relations'] = [{'from': a['id'], 'to': b['id'], 'status': 'UNKNOWN',
                        'routeIds': [], 'conditions': 'UNKNOWN'}
                       for a in gc['ports'] for b in gc['ports']]
    by_port = {p['id']: p for p in gc['ports']}
    for route in gc['routes']:
        validation_id = 'migration-' + route['id']
        route['validationIds'] = [validation_id]
        route_cases = [case for case in cases if case.get('route_spec', {}).get('id', 'main') == route['id']]
        route['requiredAbilities'] = sorted(set().union(*(set(case.get('capabilities', [])) for case in route_cases))) if route_cases else cases[0].get('capabilities', [])
        route['actionTags'] = sorted({op['op'] for case in cases
                                    if case.get('route_spec', {}).get('id', 'main') == route['id']
                                    for op in case.get('control_plan', []) if op['op'] not in ('wait', 'axis')})
        route['durationSeconds'] = 'UNKNOWN'
        route['resourceProfile'] = {'status': 'UNKNOWN'}
        route['initialConditions'] = {'status': 'UNKNOWN'}
        route['localDisplacementBlocks'] = [(b-a)/size for a, b in zip(by_port[route['from']]['position'], by_port[route['to']]['position'])]
        route['transfer']['status'] = 'observed_only'
        route['availability'] = 'UNKNOWN'
        old = copy.deepcopy(old_validations[route['id']])
        old.update(id=validation_id, result='UNKNOWN', artifacts=[],
                   method='pending_actual_godot_migration_revalidation',
                   coverage={'policy': 'pending fixed calibration, independent holdout, and boundary probes'},
                   failures=[], unverified=['not_yet_run'])
        gc['validations'].append(old)
        relation = next(r for r in gc['relations'] if r['from'] == route['from'] and r['to'] == route['to'])
        relation['status'] = 'path'
        relation['routeIds'].append(route['id'])
    for transform in gc['space']['transforms']:
        transform['status'] = 'UNKNOWN'; transform['validationIds'] = []
    gc['generation']['migration'] = dict(sourcePath=relative(folder), sourceVersion=old_version,
        sourceDocumentSha256=sha(folder/'module.mapnote.json'),
        policy='minimal_actual_boundary_adaptation', moduleId=module_id,
        legacyEvidencePolicy='Historical artifacts remain bound to their original content version.')
    from .adaptation import bind_internal_waypoints
    doc, cases, waypoint_binding = bind_internal_waypoints(doc, cases, original_cases)
    from .purpose_compat import bind as bind_compatibility
    doc, cases, compatibility_bindings = bind_compatibility(doc, cases, original_cases)
    gc = doc['generationContract']
    from .godot_package import bind_case_behavior
    doc = bind_case_behavior(doc, cases)
    from .corners import annotate
    annotate(doc)
    out.mkdir(parents=True)
    write(out / 'adaptation.json', adaptation)
    write(out / 'reference-bindings.json', dict(internalWaypoints=waypoint_binding, compatibility=compatibility_bindings))
    if gc['kind'] == 'macro':
        from .adaptation import persist_macro_components
        doc, component_receipts = persist_macro_components(folder, out, doc)
        write(out/'component-receipts.json', component_receipts)
    write(out / 'module.mapnote.json', doc)
    # Keep real inputs, discard bulky recording caches (not physics inputs).
    for case in cases:
        case.pop('recorded_frames', None)
    write(out / 'cases.json', {'cases': cases})
    write(out / 'migration.json', dict(schema='pcg/module-migration/v1', moduleId=module_id,
        sourcePath=relative(folder), sourceVersion=old_version, sourceFiles={
            str(p.relative_to(folder)): sha(p) for p in folder.rglob('*') if p.is_file()},
        status='prepared_unverified', sourceType=read(folder/'record.json').get('sourceType', 'repository_generated'),
        humanReview='design_hold' if review_status == 'human_design_hold' else 'UNKNOWN', productionAdmitted=False,
        internalGeometryChanged=adaptation.get('internalGeometryChanged', bool(adaptation.get('edits'))),
        adaptation=adaptation, evidence=[], unresolved=['boundary crossing', 'closure profiles', 'mirror', 'unverified port pairs']))
    result = contract(out / 'module.mapnote.json', refresh=True)
    return dict(status='prepared_unverified', moduleId=module_id, out=str(out), contract=result)


def validate(folder, require_certified=False):
    folder = Path(folder).resolve()
    result = contract(folder/'module.mapnote.json')
    if not result['versionMatches']:
        raise ValueError('stale_content_version')
    doc = read(folder/'module.mapnote.json'); meta = read(folder/'migration.json')
    if doc['generationContract']['version'] != 2:
        raise ValueError('formal_archive_requires_v2')
    verify_artifacts(meta['evidence'])
    for validation in doc['generationContract']['validations']:
        verify_artifacts(validation['artifacts'])
    if require_certified:
        if meta['status'] != 'passed_scoped':
            raise ValueError('not_certified_for_archive')
        gc = doc['generationContract']
        if gc['space']['actorBody']['size'] != read(STATE/'protocol.json')['bodySize']:
            raise ValueError('declared_body_does_not_match_real_Harness_body')
        verify_artifacts([gc['space']['actorBody']['source']])
        if gc['mirror']['status'] == 'verified':
            raise ValueError('mirror_physics_certificate_not_implemented_in_migration_adapter')
        if any(profile['status']=='verified' and profile['closedPorts'] for profile in gc['closures']):
            raise ValueError('closure_physics_certificate_not_implemented_in_migration_adapter')
        cases = read(folder/('physics-input-cases.json' if (folder/'physics-input-cases.json').exists() else 'cases.json'))['cases']
        actual_sets = {frozenset(case.get('capabilities', [])) for case in cases}
        for port in gc['ports']:
            if port['permission'] == 'INOUT': continue
            condition = port.get('initialPermissionConditions', {})
            mask = condition.get('availableAbilitiesExact')
            if not isinstance(mask, list) or not mask or frozenset(mask) not in actual_sets:
                raise ValueError('initial_oneway_permission_requires_actual_exact_ability_configuration:' + port['id'])
        # verify_report below rebuilds and checks every permitted direction from
        # actual raw full-body crossings; no declaration substitutes for probes.
        legacy_record = resolve_artifact(meta['sourcePath']+'/record.json')
        if sha(legacy_record) != meta['sourceFiles']['record.json']:
            raise ValueError('original_enrollment_record_changed')
        verify_artifacts(read(legacy_record).get('evidence',[]))
        routes = doc['generationContract']['routes']
        validations = doc['generationContract']['validations']
        if not routes or any(not any(v['id'] in r['validationIds'] and v['kind'] == 'physics'
                        and v['result'] == 'pass' for v in validations) for r in routes):
            raise ValueError('route_missing_current_physics_certificate')
        if not meta.get('boundaryProbe', {}).get('passed'):
            raise ValueError('port_crossing_not_validated')
        if not (folder/'godot-package.json').is_file():
            raise ValueError('godot_package_not_built')
        from .godot_package import verify_package
        verify_package(folder, require_loaded=True)
        from .physics import verify_report
        verify_report(folder, meta['physicsReport'])
    return dict(status='valid', moduleId=meta['moduleId'], contentVersion=doc['generationContract']['contentVersion'],
                certified=meta['status'] == 'passed_scoped', mapReady=False,
                certifiedClosureProfiles=[], certifiedMirror=False)


def _migration_lock():
    """Serialize the two operations that relocate originals and update the index."""
    import contextlib
    import fcntl

    @contextlib.contextmanager
    def locked():
        STATE.mkdir(parents=True, exist_ok=True)
        with (STATE/'relocation.lock').open('a+b') as stream:
            fcntl.flock(stream, fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(stream, fcntl.LOCK_UN)
    return locked()


def _tree_files(folder):
    return {str(p.relative_to(folder)): sha(p)
            for p in Path(folder).rglob('*') if p.is_file()}


def _check_tree(folder, expected, extra=()):
    actual = _tree_files(folder)
    for name in extra:
        actual.pop(name, None)
    if actual != expected:
        raise ValueError('transaction_original_or_destination_changed:' + str(folder))


def _save_transaction(path, transaction):
    # write() uses replace; fsync also makes the write-ahead record durable.
    import os
    write(path, transaction)
    with Path(path).open('rb') as stream:
        os.fsync(stream.fileno())
    descriptor = os.open(Path(path).parent, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _restore_catalog(hex_bytes):
    path = ACTIVE/'catalog.json'
    if hex_bytes is None:
        path.unlink(missing_ok=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(mode='wb', dir=path.parent, delete=False) as stream:
        stream.write(bytes.fromhex(hex_bytes))
        temporary = Path(stream.name)
    temporary.replace(path)


def _transaction_paths(transaction):
    source = (REPO/transaction['source']).resolve()
    archive = (REPO/transaction['archive']).resolve()
    destination = (REPO/transaction['destination']).resolve() if transaction.get('destination') else None
    staging = (REPO/transaction['staging']).resolve() if transaction.get('staging') else None
    if transaction.get('operation') == 'refresh_package':
        old_manifest = transaction.get('oldManifestSha256', '')
        journal_source = (REPO/transaction.get('journalKey', '')).resolve()
        if (source.parent != ACTIVE.resolve() or destination != source or staging is None
                or archive.parent != (RECYCLE/source.name).resolve()
                or not re.fullmatch('[a-f0-9]{64}', old_manifest)
                or archive.name != 'compiled-'+old_manifest
                or not original_package_path(journal_source)):
            raise ValueError('unsafe_package_refresh_paths')
    elif not original_package_path(source) or not archive.is_relative_to(RECYCLE.resolve()) or archive == RECYCLE.resolve():
        raise ValueError('unsafe_transaction_original_paths')
    if destination is not None and destination.parent != ACTIVE.resolve():
        raise ValueError('unsafe_transaction_destination')
    if staging is not None and staging.parent != (STATE/'staging').resolve():
        raise ValueError('unsafe_transaction_staging')
    receipt = transaction['receiptName']
    if Path(receipt).name != receipt or receipt in transaction['sourceFiles']:
        raise ValueError('unsafe_transaction_archive_receipt')
    return source, archive, destination, staging


def _new_transaction(operation, source, archive, journal, *, destination=None,
                     staging=None, prepared=None, journal_key=None, **identity):
    files = _tree_files(source)
    receipt = 'archive.json'
    while (source/receipt).exists():
        receipt = 'migration-' + receipt
    key = journal_key or relative(source)
    catalog = ACTIVE/'catalog.json'
    return dict(schema='pcg/relocation-transaction/v2', operation=operation,
        status='prepared', source=relative(source), journalKey=key, archive=relative(archive),
        destination=relative(destination) if destination else None,
        staging=relative(staging) if staging else None,
        sourceFiles=files, preparedFiles=_tree_files(prepared) if prepared else None,
        receiptName=receipt, previousEntry=copy.deepcopy(journal['entries'].get(key)),
        previousRelocation=journal['relocations'].get(key), ledgerExisted=JOURNAL.exists(),
        previousCatalogHex=catalog.read_bytes().hex() if catalog.exists() else None,
        **identity)


def _rollback_transaction(path, transaction):
    """Repeatable recovery, including a process killed between rename and ledger."""
    if transaction.get('operation') == 'refresh_package':
        return _rollback_package_refresh(path, transaction)
    source, archive, destination, staging = _transaction_paths(transaction)
    if source.exists() and archive.exists():
        raise ValueError('transaction_has_both_original_and_archive')
    if not source.exists() and not archive.exists():
        raise ValueError('transaction_original_missing')
    original = source if source.exists() else archive
    _check_tree(original, transaction['sourceFiles'],
                () if original == source else (transaction['receiptName'],))
    if destination and destination.exists():
        # Never remove an unrelated or subsequently edited directory.
        _check_tree(destination, transaction['preparedFiles'])
    if archive.exists():
        (archive/transaction['receiptName']).unlink(missing_ok=True)
        archive.rename(source)
    if destination and destination.exists():
        shutil.rmtree(destination)
    if staging and staging.exists():
        shutil.rmtree(staging)
    _restore_transaction_state(transaction)
    _check_tree(source, transaction['sourceFiles'])
    transaction['status'] = 'rolled_back'
    _save_transaction(path, transaction)


def _restore_transaction_state(transaction):
    journal = ledger(); key = transaction.get('journalKey', transaction['source'])
    for collection, previous in [('entries', transaction['previousEntry']),
                                 ('relocations', transaction['previousRelocation'])]:
        if previous is None:
            journal[collection].pop(key, None)
        else:
            journal[collection][key] = previous
    if not transaction['ledgerExisted'] and not journal['entries'] and not journal['relocations']:
        JOURNAL.unlink(missing_ok=True)
    else:
        write(JOURNAL, journal)
    _restore_catalog(transaction['previousCatalogHex'])


def _rollback_package_refresh(path, transaction):
    current, archive, _, staging = _transaction_paths(transaction)
    if archive.exists():
        _check_tree(archive, transaction['sourceFiles'], (transaction['receiptName'],))
        if current.exists():
            _check_tree(current, transaction['preparedFiles'])
            if staging.exists():
                raise ValueError('package_refresh_staging_conflict')
            current.rename(staging)
        (archive/transaction['receiptName']).unlink(missing_ok=True)
        archive.rename(current)
    elif current.exists():
        # Also covers a process killed after restoring the old package but
        # before rolling back its journal/index, so recovery is repeatable.
        _check_tree(current, transaction['sourceFiles'])
    else:
        raise ValueError('package_refresh_original_missing')
    if staging.exists():
        shutil.rmtree(staging)
    _restore_transaction_state(transaction)
    _check_tree(current, transaction['sourceFiles'])
    transaction['status'] = 'rolled_back'
    _save_transaction(path, transaction)


def _recover_transaction(path, expected):
    if not path.exists():
        return None
    transaction = read(path)
    if transaction.get('schema') != 'pcg/relocation-transaction/v2':
        raise ValueError('legacy_transaction_requires_manual_recovery')
    if any(transaction.get(key) != value for key, value in expected.items()):
        raise ValueError('transaction_identity_conflict')
    _transaction_paths(transaction)
    if transaction['status'] not in ('complete', 'rolled_back'):
        _rollback_transaction(path, transaction)
    return transaction


def _relocate_transaction(path, transaction, journal, entry, *, prepared=None):
    source, archive, destination, staging = _transaction_paths(transaction)
    # Persist before copying or moving any original/target bytes.
    _save_transaction(path, transaction)
    try:
        if destination:
            staging.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(prepared, staging)
            _check_tree(staging, transaction['preparedFiles'])
            validate(staging, require_certified=True)
            if destination.exists():
                raise ValueError('transaction_destination_appeared')
            destination.parent.mkdir(parents=True, exist_ok=True)
            staging.rename(destination)
            validate(destination, require_certified=True)
        archive.parent.mkdir(parents=True, exist_ok=True)
        _check_tree(source, transaction['sourceFiles'])
        source.rename(archive)
        _check_tree(archive, transaction['sourceFiles'])
        journal['relocations'][transaction['source']] = relative(archive)
        journal['entries'][transaction['source']] = entry
        verify_artifacts([dict(path=transaction['source']+'/'+name, sha256=digest)
                          for name, digest in transaction['sourceFiles'].items()], journal)
        write(archive/transaction['receiptName'], dict(
            reason=entry['archiveReason'], originalFiles=transaction['sourceFiles'],
            replacement=relative(destination) if destination else None,
            reasonRecord=entry.get('reasonRecord')))
        write(JOURNAL, journal)
        build_catalog()
        transaction['status'] = 'complete'
        _save_transaction(path, transaction)
    except BaseException:
        # A killed process cannot run this handler; the next invocation replays
        # the same rollback from the still-pending write-ahead record.
        _rollback_transaction(path, transaction)
        raise


def promote(folder):
    with _migration_lock():
        return _promote_locked(folder)


def _promote_locked(folder):
    folder = Path(folder).resolve()
    meta = read(folder/'migration.json'); module_id = safe_id(meta['moduleId'])
    source = (REPO/meta['sourcePath']).resolve()
    if not original_package_path(source) or relative(source) != meta['sourcePath']:
        raise ValueError('only_inventoried_repository_sources_may_be_promoted')
    destination = ACTIVE/module_id
    source_version = meta['sourceVersion'].removeprefix('sha256:')
    if not re.fullmatch('[a-f0-9]{64}', source_version):
        raise ValueError('invalid_original_content_version')
    archive = RECYCLE/module_id/source_version
    transaction = STATE/'transactions'/f'{module_id}.json'
    identity = dict(operation='promote', source=relative(source),
                    destination=relative(destination), archive=relative(archive),
                    contentVersion=read(folder/'module.mapnote.json')['generationContract']['contentVersion'])
    recovered = _recover_transaction(transaction, identity)
    validated = validate(folder, require_certified=True)
    if (folder/'cases.json').exists():
        _check_available_metadata(folder)
    journal = ledger(); existing = journal['entries'].get(meta['sourcePath'], {})
    if destination.exists():
        current = validate(destination, require_certified=True)
        if (current['contentVersion'] == validated['contentVersion']
                and existing.get('migrationStatus') == 'active'
                and not source.exists() and archive.is_dir()
                and journal['relocations'].get(meta['sourcePath']) == relative(archive)):
            _check_tree(archive, meta['sourceFiles'],
                        (recovered['receiptName'],) if recovered else ('archive.json',))
            build_catalog()
            return dict(status='already_active', moduleId=module_id)
        raise ValueError('current_module_exists_use_explicit_revision_workflow')
    if recovered and recovered['status'] == 'complete':
        raise ValueError('completed_transaction_state_conflict')
    if archive.exists() or not source.is_dir():
        raise ValueError('source_or_archive_state_conflict')
    for rel, digest in meta['sourceFiles'].items():
        if sha(source/rel) != digest:
            raise ValueError('source_changed_since_preparation:' + rel)
    if set(meta['sourceFiles']) != {str(p.relative_to(source)) for p in source.rglob('*') if p.is_file()}:
        raise ValueError('source_file_set_changed')
    staging = STATE/'staging'/module_id
    if staging.exists():
        raise ValueError('unowned_transaction_staging_exists')
    value = _new_transaction('promote', source, archive, journal,
        destination=destination, staging=staging, prepared=folder,
        contentVersion=validated['contentVersion'], moduleId=module_id)
    entry = {**existing, 'migrationStatus': 'active',
        'moduleId': module_id, 'destination': relative(destination), 'archive': relative(archive),
        'sourceVersion': meta['sourceVersion'], 'contentVersion': validated['contentVersion'],
        'sourceType': meta.get('sourceType', 'repository_generated'),
        'humanReview': meta['humanReview'], 'archiveReason': 'successfully_migrated_original',
        'archiveReceipt': relative(archive/value['receiptName'])}
    _relocate_transaction(transaction, value, journal, entry, prepared=folder)
    return dict(status='active', moduleId=module_id, archived=relative(archive))


def archive(folder, reason, replacement=None):
    """Only explicit disposal/deduplication; a failed migration is not disposal."""
    with _migration_lock():
        return _archive_locked(folder, reason, replacement)


def _archive_locked(folder, reason, replacement=None):
    if reason not in ('explicitly_discarded', 'exact_duplicate'):
        raise ValueError('failure_and_near_duplicate_must_stay_in_place')
    folder = Path(folder).resolve()
    if not original_package_path(folder):
        raise ValueError('only_original_module_package_can_be_archived')
    if reason == 'exact_duplicate':
        if not replacement:
            raise ValueError('deduplication_requires_reviewed_equivalence_record')
        # A reason inside the original can be temporarily absent after a
        # pre-ledger process death. Recover the write-ahead move first below.
        preliminary = resolve_artifact(replacement)
        if preliminary.is_file() and read(preliminary).get('schema') != 'pcg/exact-module-equivalence/v1':
            raise ValueError('deduplication_requires_reviewed_equivalence_record')
    if not replacement:
        raise ValueError('explicit_disposal_requires_reason_record_path')
    target = RECYCLE/'discarded'/folder.name
    source = relative(folder)
    transaction = STATE/'transactions'/('discard-'+hashlib.sha256(source.encode()).hexdigest()+'.json')
    identity = dict(operation='discard', source=source, destination=None,
                    archive=relative(target), reasonRecord=replacement)
    recovered = _recover_transaction(transaction, identity)
    # A reason artifact may itself be inside the moved package. Recover the
    # relocation before resolving it, especially after a pre-ledger crash.
    reason_path = resolve_artifact(replacement)
    if not reason_path.is_file():
        raise ValueError('disposal_reason_record_missing')
    if recovered and sha(reason_path) != recovered['reasonRecordSha256']:
        raise ValueError('disposal_reason_record_changed')
    duplicate = {}
    if reason == 'exact_duplicate':
        from .equivalence import verify
        duplicate = verify(folder,read(reason_path))
    journal = ledger()
    if recovered and recovered['status'] == 'complete':
        if (folder.exists() or not target.is_dir()
                or journal['entries'].get(source, {}).get('migrationStatus') != 'recycled'
                or journal['relocations'].get(source) != relative(target)):
            raise ValueError('completed_transaction_state_conflict')
        _check_tree(target, recovered['sourceFiles'], (recovered['receiptName'],))
        build_catalog()
        return dict(status='already_recycled', archive=relative(target))
    if not folder.is_dir():
        raise ValueError('only_original_module_package_can_be_archived')
    if target.exists():
        raise ValueError('archive_exists')
    value = _new_transaction('discard', folder, target, journal,
        reasonRecord=replacement, reasonRecordSha256=sha(reason_path))
    entry = dict(migrationStatus='recycled', archive=relative(target), **duplicate,
                 archiveReason=reason, reasonRecord=replacement,
                 archiveReceipt=relative(target/value['receiptName']))
    _relocate_transaction(transaction, value, journal, entry)
    return dict(status='recycled', archive=relative(target))


def refresh_package(prepared_folder, *, evidence_update=False):
    """Refresh compiled output; explicit evidence correction has a narrow proof."""
    with _migration_lock():
        return _refresh_package_locked(Path(prepared_folder).resolve(), evidence_update=evidence_update)


def _refresh_package_locked(folder, *, evidence_update=False):
    meta = read(folder/'migration.json'); module_id = safe_id(meta['moduleId'])
    current = ACTIVE/module_id
    new_manifest = sha(folder/'godot-package.json')
    content_version = read(folder/'module.mapnote.json')['generationContract']['contentVersion']
    legacy_source = (REPO/meta['sourcePath']).resolve()
    if not original_package_path(legacy_source) or relative(legacy_source) != meta['sourcePath']:
        raise ValueError('package_refresh_requires_original_legacy_identity')
    key = meta['sourcePath']
    transaction_path = STATE/'transactions'/f'refresh-{module_id}-{new_manifest}.json'
    identity = dict(operation='refresh_package', source=relative(current),
                    destination=relative(current), journalKey=key, moduleId=module_id,
                    contentVersion=content_version, newManifestSha256=new_manifest)
    if evidence_update:
        identity['evidenceUpdate'] = True
    # Restore a prior interrupted attempt before any evidence verifier needs
    # paths under the temporarily absent current package.
    recovered = _recover_transaction(transaction_path, identity)
    ready = validate(folder, require_certified=True)
    old = validate(current, require_certified=True)
    old_meta = read(current/'migration.json')
    if ready['moduleId'] != module_id or old['moduleId'] != module_id:
        raise ValueError('package_refresh_module_id_changed')
    if ready['contentVersion'] != old['contentVersion'] or old['contentVersion'] != content_version:
        raise ValueError('package_refresh_content_version_changed')
    evidence_proof = None
    if sha(folder/'module.mapnote.json') != sha(current/'module.mapnote.json'):
        if not evidence_update:
            raise ValueError('package_refresh_module_document_changed')
        from .evidence_refresh import prove_available_correction
        evidence_proof = prove_available_correction(current, folder)
    # A compiler update cannot silently replace physics, original identity, or
    # human review. godotLoad is intentionally allowed to bind the new replay.
    for field in ('sourcePath', 'sourceVersion', 'sourceFiles', 'physicsReport',
                  'humanReview', 'productionAdmitted'):
        if meta.get(field) != old_meta.get(field):
            raise ValueError('package_refresh_metadata_changed:' + field)
    journal = ledger(); existing = journal['entries'].get(key, {})
    if (existing.get('migrationStatus') != 'active'
            or existing.get('moduleId') != module_id
            or existing.get('destination') != relative(current)
            or existing.get('contentVersion') != content_version):
        raise ValueError('package_refresh_current_not_in_active_ledger')
    old_manifest = sha(current/'godot-package.json')
    if old_manifest == new_manifest:
        if recovered and recovered['status'] == 'complete':
            _, archived, _, _ = _transaction_paths(recovered)
            _check_tree(archived, recovered['sourceFiles'], (recovered['receiptName'],))
            if not any(h.get('transaction') == relative(transaction_path)
                       and h.get('manifestSha256') == new_manifest
                       for h in existing.get('packageHistory', [])):
                raise ValueError('completed_package_refresh_history_missing')
        build_catalog()
        return dict(status='already_current', moduleId=module_id,
                    contentVersion=content_version, manifestSha256=new_manifest)
    if recovered and recovered['status'] == 'complete':
        raise ValueError('completed_package_refresh_state_conflict')
    if folder.is_relative_to(ACTIVE) or folder.is_relative_to(RECYCLE):
        raise ValueError('package_refresh_ready_folder_must_be_outside_archives')
    archive = RECYCLE/module_id/('compiled-'+old_manifest)
    staging = STATE/'staging'/f'refresh-{module_id}-{new_manifest[:16]}'
    if archive.exists() or staging.exists():
        raise ValueError('package_refresh_archive_or_staging_conflict')
    transaction = _new_transaction('refresh_package', current, archive, journal,
        destination=current, staging=staging, prepared=folder, journal_key=key,
        contentVersion=content_version, moduleId=module_id,
        oldManifestSha256=old_manifest, newManifestSha256=new_manifest,
        **(dict(evidenceUpdate=True, evidenceUpdateProof=evidence_proof) if evidence_update else {}))
    history = copy.deepcopy(existing.get('packageHistory', []))
    history.append(dict(contentVersion=content_version,
        previousManifestSha256=old_manifest, manifestSha256=new_manifest,
        archivedPackage=relative(archive), archiveReceipt=relative(archive/transaction['receiptName']),
        transaction=relative(transaction_path)))
    if evidence_update:
        history[-1].update(evidenceUpdate=True, evidenceUpdateProof=evidence_proof)
    updated = {**existing, 'packageHistory': history}
    _save_transaction(transaction_path, transaction)
    try:
        staging.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(folder, staging)
        _check_tree(staging, transaction['preparedFiles'])
        validate(staging, require_certified=True)
        _check_tree(current, transaction['sourceFiles'])
        archive.parent.mkdir(parents=True, exist_ok=True)
        current.rename(archive)
        _check_tree(archive, transaction['sourceFiles'])
        staging.rename(current)
        validate(current, require_certified=True)
        write(archive/transaction['receiptName'], dict(reason='compiled_package_refreshed',
            replacement=relative(current), contentVersion=content_version,
            previousManifestSha256=old_manifest, manifestSha256=new_manifest,
            originalFiles=transaction['sourceFiles']))
        # Original legacy relocations still resolve to the original archive;
        # this operation records compiled-package history only.
        journal['entries'][key] = updated
        write(JOURNAL, journal)
        build_catalog()
        transaction['status'] = 'complete'
        _save_transaction(transaction_path, transaction)
    except BaseException:
        _rollback_transaction(transaction_path, transaction)
        raise
    return dict(status='package_refreshed', moduleId=module_id,
                contentVersion=content_version, manifestSha256=new_manifest,
                archived=relative(archive))


def build_catalog():
    if _CATALOG_DEFERRED:
        return dict(status='deferred_until_batch_end')
    rows = []
    for folder in sorted(ACTIVE.iterdir() if ACTIVE.exists() else []):
        if not folder.is_dir() or not (folder/'module.mapnote.json').exists():
            continue
        validated = validate(folder, require_certified=True)
        doc = read(folder/'module.mapnote.json'); meta = read(folder/'migration.json')
        gc = doc['generationContract']; module_id = safe_id(meta['moduleId'])
        if folder.name != module_id or any(row['id']==module_id for row in rows):
            raise ValueError('current_directory_must_match_unique_stable_module_id')
        source_kind = doc.get('source', {}).get('kind')
        category = doc.get('source', {}).get('category')
        if not category:
            category = '森林' if source_kind == 'forest' else '工坊组合' if source_kind == 'foundry' else ('平原' if doc.get('source', {}).get('moduleId', '').startswith('plains_') else '通用') if meta.get('sourceType') == 'original_game' else '平原'
        native_profile = gc.get('requiredNativeProfile') or gc['generation'].get('parameters', {}).get('original_tuning_profile')
        from .corners import verified_receipts
        corner_receipts = verified_receipts(module_id, sha(folder/'module.mapnote.json'), gc['contentVersion'])
        from .corners import compiled_ports
        consumer_ports = compiled_ports(doc, corner_receipts)
        rows.append(dict(id=module_id, moduleId=doc['id'], title=doc['title'],
            cornerConfigurationReceipts=corner_receipts,
            contentVersion=validated['contentVersion'], file=f'./modules/{module_id}/module.mapnote.json',
            thumbnail=f'./modules/{module_id}/thumbnail.svg', contentSha256=sha(folder/'module.mapnote.json'),
            portCount=len(gc['ports']), category=category, sourceType=meta.get('sourceType', 'repository_generated'),
            requiredNativeProfile=native_profile,
            capabilityRequirements=doc['capabilityRequirements'], difficulty=doc['difficulty'],
            humanReview=meta['humanReview'], technicalStatus=meta['status'], mapReady=False,
            foundation=gc['foundation'],
            sceneOriginOffsetPixels=[-gc['space']['bounds']['x'],-gc['space']['bounds']['y']],
            ports=consumer_ports,
            portConfigurations=gc.get('portConfigurations', []),
            routes=[{k: r[k] for k in ('id','from','to','requiredAbilities')} for r in gc['routes']],
            unresolved=meta['unresolved']))
    value = dict(schema='map-notes/module-archive/v1', foundationVersion='1.0',
        updateRef='content/task-a-workshop', modules=rows,
        aliasFile='./modules/aliases.json',
        warning='Technical scoped admission is not human approval or unrestricted Map certification.')
    write(ACTIVE/'catalog.json', value)
    return value


def _check_available_metadata(folder):
    folder = Path(folder)
    doc = read(folder/'module.mapnote.json')
    cases = read(folder/('physics-input-cases.json' if (folder/'physics-input-cases.json').exists() else 'cases.json'))['cases']
    for validation in doc['generationContract']['validations']:
        if validation['kind'] != 'physics' or validation['result'] != 'pass': continue
        relevant = [case for case in cases if case.get('route_spec',{}).get('id','main') == validation['routeId']]
        if not relevant or any(set(case.get('capabilities', [])) != set(validation['capabilityConfiguration']['available']) for case in relevant):
            raise ValueError('physics_evidence_available_abilities_do_not_match_real_input:' + validation['routeId'])


def certify(folder, report_path):
    """Attach rechecked results; an input boolean cannot certify a Module."""
    from .physics import verify_report
    folder = Path(folder).resolve()
    proof = dict(path=relative(report_path), sha256=sha(report_path))
    report = verify_report(folder, proof)
    doc = read(folder/'module.mapnote.json')
    actual_cases = read(folder/('physics-input-cases.json' if (folder/'physics-input-cases.json').exists() else 'cases.json'))['cases']
    for validation in doc['generationContract']['validations']:
        route_cases = [case for case in actual_cases if case.get('route_spec',{}).get('id','main') == validation['routeId']]
        if not route_cases or len({frozenset(case.get('capabilities',[])) for case in route_cases}) != 1:
            raise ValueError('ambiguous_actual_provided_capability_configuration')
        validation['capabilityConfiguration']['available'] = list(route_cases[0].get('capabilities', []))
        validation.update(result='pass', method='offline_reanalysis_of_actual_godot_evidence'if report.get('offlineAnalysis')else'actual_godot_fixed_migration_protocol',
            artifacts=[proof, report['sourceBinding'], report['batches'], report['protocol'], report['probes']],
            coverage={'policy': 'Original interior quality gates plus full-body boundary and continuous exit',
                      'route': next(r for r in report['routes'] if r['routeId'] == validation['routeId']),
                      'arbitraryEntryStates': 'UNKNOWN', 'fullMap': 'UNKNOWN'},
            unverified=report['unknown'])
    write(folder/'module.mapnote.json', doc)
    contract(folder/'module.mapnote.json', refresh=True)
    meta = read(folder/'migration.json')
    meta.update(status='passed_scoped', physicsReport=proof,
                boundaryProbe={'passed': True, 'artifact': report['probes']},
                evidence=[proof, report['sourceBinding'], report['batches'], report['protocol'], report['probes']],
                unresolved=copy.deepcopy(report['unknown']))
    write(folder/'migration.json', meta)
    _check_available_metadata(folder)
    return dict(status='passed_scoped', moduleId=meta['moduleId'], actualAttempts=report['actualAttempts'])


def package(folder, out):
    """Compile and actually load the pinned data package before promotion."""
    from .godot_package import compile_package, run_package_validation
    folder = Path(folder).resolve(); out = Path(out).resolve()
    meta = read(folder/'migration.json')
    if meta['status'] != 'passed_scoped':
        raise ValueError('physics_certification_required_before_package')
    # Freeze actual successful calibration inputs for native playback. Geometry
    # and program bytes stay identical; recorded_frames is evidence only.
    source = folder/'replay-cases.json'
    if source.exists():
        canonical = read(folder/'physics-input-cases.json' if (folder/'physics-input-cases.json').exists() else folder/'cases.json')['cases']
        playback = read(source)['cases']
        def inputs(case):
            case = copy.deepcopy(case); case.pop('recorded_frames', None); return case
        if [inputs(c) for c in canonical] != [inputs(c) for c in playback]:
            raise ValueError('canonical_replay_inputs_differ_from_validated_cases')
    elif meta.get('physicsReport'):
        import gzip
        report_path = resolve_artifact(meta['physicsReport']['path'])
        report = read(report_path); run = report_path.parent
        canonical = read(folder/'physics-input-cases.json' if (folder/'physics-input-cases.json').exists() else folder/'cases.json')
        playback = copy.deepcopy(canonical)
        if any(c.get('moving_platforms') or c.get('enemies') or c.get('saws') for c in canonical['cases']):
            raise ValueError('dynamic_package_requires_actual_canonical_clean_replay')
        batches = {batch['batch']: batch for batch in read(resolve_artifact(report['batches']['path']))}
        for case, route in zip(playback['cases'], report['routes']):
            evaluation = read(resolve_artifact(route['calibration']['path']))
            clean = next(row for row in evaluation['rows'] if row['level'] == 'clean' and row['trial'] == 0)
            ev = clean['evidence']; batch = batches[ev['batch']]
            with gzip.open(run/batch['gzip_path'], 'rt') as stream:
                raw = __import__('json').load(stream)['results'][ev['index']]
            case['recorded_frames'] = [dict(frame=f['frame'], axis=f['axis'], requested=f['requested']) for f in raw['frames']]
        write(source, playback)
    else:
        source = resolve_artifact(meta['sourcePath']+'/cases.json')
    if not source.exists():
        raise ValueError('actual_successful_playback_cases_missing')
    compile_package(folder/'module.mapnote.json', source, out, stable_id=meta['moduleId'])
    if (folder/'components').exists():
        shutil.copytree(folder/'components', out/'components')
        if (folder/'component-receipts.json').exists():
            shutil.copy2(folder/'component-receipts.json', out/'component-receipts.json')
    physics_input = folder/'physics-input-cases.json'
    shutil.copy2(physics_input if physics_input.exists() else folder/'cases.json', out/'physics-input-cases.json')
    write(out/'migration.json', meta)
    shutil.copy2(folder/'thumbnail.svg', out/'thumbnail.svg')
    loaded = run_package_validation(out)
    meta['godotLoad'] = dict(passed=loaded['loaded'], evidence='load-evidence/index.json',
                             scope='actual replay of every frozen canonical case on the declared runtime')
    write(out/'migration.json', meta)
    validate(out, require_certified=True)
    return dict(status='package_loaded', moduleId=meta['moduleId'], out=str(out), load=loaded)
