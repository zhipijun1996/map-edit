"""Resume fixed corner-interface batches using the existing Godot Harness.

Preparation and clean diagnostics never grant Port permissions. Only the same
full quality verifier and real native playback can publish a v2 configuration.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil

from . import core, corners

POLICY = 'preserve_geometry_no_extra_closure'


def _artifact(path):
    return dict(path=core.relative(path), sha256=core.sha(path))


def _key(module_id, port_id, corner):
    raw = json.dumps([module_id, port_id, corner], separators=(',', ':'))
    return module_id[:48] + '-' + hashlib.sha256(raw.encode()).hexdigest()[:16]


def _paths(name):
    core.safe_id(name)
    if len(name) > 64:
        raise ValueError('corner_batch_name_must_not_exceed_64_characters')
    state = core.STATE/'corner-batches'/name
    prepared = core.REPO/'.cache/migration/corner-batches'/name/'prepared'
    return state, prepared


def inventory_options(catalog=None, repo=None, *, include_certified=False):
    """Enumerate actual current versions, never old candidates or seed counts."""
    repo = Path(repo or core.REPO).resolve()
    catalog = catalog if catalog is not None else core.read(repo/'modules/catalog.json')
    rows = []
    for entry in sorted(catalog['modules'], key=lambda e:e['id']):
        folder = repo/'modules'/core.safe_id(entry['id'])
        docpath = folder/'module.mapnote.json'; doc = core.read(docpath)
        if core.sha(docpath) != entry['contentSha256']:
            raise ValueError('corner_batch_catalog_document_changed:'+entry['id'])
        gc = doc['generationContract']
        if gc['contentVersion'] != entry['contentVersion']:
            raise ValueError('corner_batch_catalog_version_changed:'+entry['id'])
        # An installed configuration can precede the final expensive catalog
        # rebuild. Durable verified receipts still prevent retesting that option.
        certified = set()
        if not include_certified and any((folder/'port-configurations').glob('*/receipt.json')):
            for ref in corners.verified_receipts(entry['id'], entry['contentSha256'], entry['contentVersion']):
                receipt = core.read(repo/ref['path'])
                certified.update((r['portId'],r['corner']) for r in receipt['relocations'])
        inputs = folder/'physics-input-cases.json'
        if not inputs.exists(): inputs = folder/'cases.json'
        indexed = {p['id']:p for p in entry.get('ports', [])}
        for port in sorted(gc['ports'], key=lambda p:p['id']):
            for corner, option in corners.options(doc, port).items():
                published = indexed.get(port['id'], {}).get('cornerRelocations', {}).get(corner, {})
                if not option['applicable'] or (not include_certified and
                        (published.get('allowed') is True or (port['id'],corner) in certified)):
                    continue
                rows.append(dict(key=_key(entry['id'], port['id'], corner), moduleId=entry['id'],
                    portId=port['id'], corner=corner, targetFace=option['targetFace'],
                    source=(folder.relative_to(repo)).as_posix(),
                    baseDocumentSha256=core.sha(docpath), baseContentVersion=gc['contentVersion'],
                    basePhysicsInputSha256=core.sha(inputs), proposedSurface=option['proposedSurface']))
    return sorted(rows, key=lambda r:(r['moduleId'], r['portId'], r['corner']))


def _verify_base(row):
    base = core.REPO/row['source']; doc = core.read(base/'module.mapnote.json')
    inputs = base/'physics-input-cases.json'
    if not inputs.exists(): inputs = base/'cases.json'
    if (core.sha(base/'module.mapnote.json') != row['baseDocumentSha256']
            or doc['generationContract']['contentVersion'] != row['baseContentVersion']
            or core.sha(inputs) != row['basePhysicsInputSha256']):
        raise ValueError('frozen_corner_base_changed:'+row['key'])
    return base


def _verify_prepared(row, *, allow_certified=False):
    folder = core.REPO/row['prepared']
    if core.sha(folder/'cases.json') != row['casesSha256']:
        raise ValueError('frozen_corner_cases_changed:'+row['key'])
    doc = core.read(folder/'module.mapnote.json')
    if doc['generationContract']['contentVersion'] != row['contentVersion']:
        raise ValueError('frozen_corner_content_version_changed:'+row['key'])
    if not allow_certified and core.sha(folder/'module.mapnote.json') != row['documentSha256']:
        raise ValueError('frozen_corner_document_changed:'+row['key'])
    return folder


def _save(path, value):
    rows = value.get('rows', [])
    value['counts'] = dict(Counter(r['status'] for r in rows))
    value['actualAttempts'] = sum(r.get('actualAttempts', 0) for r in rows)
    core.write(path, value)


def prepare(name, *, adapter_version='v2', include_certified=False, only_keys=None):
    if adapter_version == 'v2':
        from . import corner_batch_adapter as adapter
    elif adapter_version == 'v3':
        from . import corner_batch_adapter_v3 as adapter
    elif adapter_version == 'v4':
        from . import corner_batch_adapter_v4 as adapter
    else:
        raise ValueError('corner_adapter_version_must_be_v2_v3_or_v4')
    selected_keys = sorted(set(only_keys)) if only_keys is not None else None
    if selected_keys == []: raise ValueError('corner_preparation_subset_must_not_be_empty')
    dependencies = [_artifact(Path(path)) for path in sorted(set(getattr(adapter,'SOURCE_DEPENDENCIES',[])),key=str)]
    state, root = _paths(name)
    planpath = state/'plan.json'; preparation = state/'preparation.json'
    if planpath.exists():
        plan = core.read(planpath)
        if (plan.get('adapterVersion','v2') != adapter_version
                or plan.get('onlyKeys') != selected_keys
                or plan['includeCertified'] != include_certified
                or plan['adapterSource']['sha256'] != core.sha(adapter.__file__)):
            raise ValueError('frozen_corner_preparation_policy_or_adapter_changed')
        if 'implementationDependencies' in plan and plan['implementationDependencies'] != dependencies:
            raise ValueError('frozen_corner_adapter_dependencies_changed')
    else:
        rows = inventory_options(include_certified=include_certified)
        if selected_keys is not None:
            if not set(selected_keys) <= {r['key']for r in rows}:
                raise ValueError('corner_preparation_requested_key_not_in_inventory')
            rows = [r for r in rows if r['key'] in selected_keys]
        plan = dict(schema='pcg/corner-batch-plan/v2', name=name,
            retiredSidePolicy=POLICY, includeCertified=include_certified, adapterVersion=adapter_version,
            onlyKeys=selected_keys, implementationDependencies=dependencies,
            options=rows, adapterSource=_artifact(Path(adapter.__file__)),
            protocol=_artifact(core.STATE/'protocol-full-v2.json'),
            maximumAttempts=core.read(core.STATE/'protocol-full-v2.json')['maximumAttemptsThisBatch'],
            adaptiveRevisions=0, selection='Stable Module/Port/corner order; retain every result; no held-out selection.')
        core.write(planpath, plan)
    outcome = core.read(preparation) if preparation.exists() else dict(
        schema='pcg/corner-batch-preparation/v2', name=name, rows=[], technicalAdmission=False)
    completed = {r['key']:r for r in outcome['rows']}
    for option in plan['options']:
        _verify_base(option)
        if option['key'] in completed:
            old = completed[option['key']]
            if old['status'] == 'prepared': _verify_prepared(old)
            continue
        row = dict(option, status='tooling_gap', actualAttempts=0)
        target = root/option['key']
        try:
            if target.exists():
                raise ValueError('unrecorded_corner_preparation_preserved_for_review')
            adapter.prepare(core.REPO/option['source'], target, option['portId'], option['corner'])
            doc = core.read(target/'module.mapnote.json')
            row.update(status='prepared', prepared=core.relative(target),
                documentSha256=core.sha(target/'module.mapnote.json'), casesSha256=core.sha(target/'cases.json'),
                contentVersion=doc['generationContract']['contentVersion'],
                adaptation=_artifact(target/'corner-adaptation.json'))
        except Exception as error:
            row['conflict'] = str(error)
        outcome['rows'].append(row); _save(preparation, outcome)
    outcome['complete'] = len(outcome['rows']) == len(plan['options'])
    _save(preparation, outcome)
    freeze = state/'frozen-inputs.json'
    value = dict(schema='pcg/corner-batch-frozen-inputs/v2', plan=_artifact(planpath),
        preparation=_artifact(preparation), rows=outcome['rows'])
    if freeze.exists() and core.read(freeze) != value:
        raise ValueError('frozen_corner_inputs_cannot_be_replaced')
    if not freeze.exists(): core.write(freeze, value)
    return outcome


def _run_name(name, stage, key):
    return name+'-'+stage+'-'+hashlib.sha256(key.encode()).hexdigest()[:16]


def _attempts(run_dir):
    batches = run_dir/'batches.json'
    return sum(r['cases'] for r in core.read(batches)) if batches.exists() else 0


def preflight(name, workers=2, only_keys=None):
    """Real clean, body seams, continuous routes and existing cheap counters."""
    from . import physics
    if workers not in (1, 2, 3): raise ValueError('corner_workers_must_be_between_one_and_three')
    state, _ = _paths(name); frozen = core.read(state/'frozen-inputs.json')
    core.verify_artifacts([frozen['plan'], frozen['preparation']])
    plan = core.read(state/'plan.json'); target = state/'preflight.json'
    outcome = core.read(target) if target.exists() else dict(
        schema='pcg/corner-batch-preflight/v2', name=name, frozenInputs=_artifact(state/'frozen-inputs.json'),
        rows=[], technicalAdmission=False, fixedWorkers=workers)
    completed = {r['key'] for r in outcome['rows']}
    requested = set(only_keys) if only_keys is not None else None
    if requested is not None and not requested <= {r['key'] for r in frozen['rows'] if r['status']=='prepared'}:
        raise ValueError('corner_preflight_requested_key_not_in_frozen_preparation')
    def execute(candidate):
        row = dict(key=candidate['key'], moduleId=candidate['moduleId'], portId=candidate['portId'],
            corner=candidate['corner'], status='tooling_gap', actualAttempts=0)
        run_name = _run_name(name, 'pre', candidate['key']); run_dir = core.REPO/'pcg/results'/run_name
        try:
            _verify_base(candidate); folder = _verify_prepared(candidate)
            report = run_dir/'clean-preflight.json'
            if run_dir.exists():
                if not report.exists():
                    raise ValueError('interrupted_corner_preflight_preserved_not_rerun')
                result = core.read(report)
                if result['contentVersion'] != candidate['contentVersion']:
                    raise ValueError('existing_corner_preflight_has_other_version')
            else:
                result = physics.run_clean(folder, run_name)
            row.update(status='preflight_passed' if result['passed'] else 'preflight_failed',
                actualAttempts=result['actualAttempts'], report=_artifact(report),
                routeFailures=[r for r in result['routes'] if not r['check']['ok']],
                probeFailures=[p for p in result['probes'] if not p['check']['passed']],
                invalidatingCounters=[c for c in result['counters'] if c['adjudication']['invalidates_design']],
                preparationError=result['preparationError'])
            replay = run_dir/'replay-cases.json'
            if replay.exists(): row['replayCases'] = _artifact(replay)
        except Exception as error:
            row.update(conflict=str(error), actualAttempts=_attempts(run_dir))
        return row
    candidates = [r for r in frozen['rows'] if r['status']=='prepared' and r['key'] not in completed
                  and (requested is None or r['key'] in requested)]
    # All submitted inputs are immutable; only main-thread receipt writes mutate.
    with ThreadPoolExecutor(max_workers=workers) as pool:
        jobs = [pool.submit(execute, row) for row in candidates]
        for job in as_completed(jobs):
            row = job.result()
            outcome['rows'].append(row); outcome['rows'].sort(key=lambda r:r['key'])
            _save(target, outcome)
            if outcome['actualAttempts'] > plan['maximumAttempts']:
                raise ValueError('frozen_corner_batch_attempt_budget_exceeded')
            print(json.dumps({k:v for k,v in row.items()
                if k not in ('routeFailures','probeFailures','invalidatingCounters')}, ensure_ascii=False), flush=True)
    outcome['complete'] = len(outcome['rows']) == sum(r['status']=='prepared' for r in frozen['rows'])
    _save(target, outcome)
    return outcome


def install_configuration(candidate, preflight_row, report_path, name):
    """Publish after real quality/native success; never move or edit the base."""
    from . import physics
    base = _verify_base(candidate)
    prepared = _verify_prepared(candidate, allow_certified=True)
    meta = core.read(prepared/'migration.json')
    configuration_id = core.safe_id(meta['cornerConfiguration']['id'])
    destination = base/'port-configurations'/configuration_id
    if destination.exists():
        reference = _artifact(destination/'receipt.json')
        if reference not in corners.verified_receipts(candidate['moduleId'], candidate['baseDocumentSha256'], candidate['baseContentVersion']):
            raise ValueError('existing_corner_configuration_not_verified')
        return dict(configurationId=configuration_id, receipt=reference, alreadyInstalled=True)
    core.verify_artifacts([preflight_row['report'], preflight_row['replayCases']])
    report = core.read(report_path)
    if not report['passed'] or report['contentVersion'] != candidate['contentVersion']:
        raise ValueError('corner_full_quality_not_passed')
    proof = _artifact(report_path)
    physics.verify_report(prepared, proof)
    # Keep the complete preflight/preparation byte images immutable. Certificate
    # annotations belong to a working copy, not the frozen batch input folder.
    certified = prepared.parent.parent/'certified'/candidate['key']
    if not certified.exists(): shutil.copytree(prepared, certified)
    _verify_prepared({**candidate, 'prepared':core.relative(certified)}, allow_certified=True)
    shutil.copy2(core.REPO/preflight_row['replayCases']['path'], certified/'replay-cases.json')
    core.certify(certified, report_path)
    staging = prepared.parent.parent/'packages'/candidate['key']
    if staging.exists():
        # A partial native attempt is evidence, not permission to retry it.
        from .godot_package import verify_package
        verify_package(staging, require_loaded=True)
    else:
        core.package(certified, staging)
    target_doc = core.read(staging/'module.mapnote.json')
    selected = next(p for p in target_doc['generationContract']['ports'] if p['id']==candidate['portId'])
    adaptation = core.read(prepared/'corner-adaptation.json')
    adaptation['frozenExperimentDocumentSha256'] = candidate['documentSha256']
    adaptation['targetDocumentSha256'] = core.sha(staging/'module.mapnote.json')
    core.write(staging/'corner-adaptation.json', adaptation)
    shutil.copy2(prepared/'corner-protocol.json', staging/'corner-protocol.json')
    def future(filename):
        return dict(path=core.relative(destination/filename), sha256=core.sha(staging/filename))
    receipt = dict(schema='pcg/corner-port-configuration/v2', moduleId=candidate['moduleId'],
        configurationId=configuration_id, retiredSidePolicy=POLICY,
        baseContentVersion=candidate['baseContentVersion'], baseDocumentSha256=candidate['baseDocumentSha256'],
        basePhysicsInputSha256=candidate['basePhysicsInputSha256'],
        relocations=[dict(portId=candidate['portId'], corner=candidate['corner'], targetFace=selected['face'],
            targetPosition=selected['position'], surface=selected['surface'], permission=selected['permission'])],
        configuration={**future('module.mapnote.json'), 'contentVersion':target_doc['generationContract']['contentVersion']},
        physicsReport=proof, package=future('godot-package.json'), adaptation=future('corner-adaptation.json'),
        allowed=True, technicalStatus='verified', humanReview='UNKNOWN', actualAttempts=report['actualAttempts'],
        scope='One full-physics/native-certified open-side configuration; no automatic joint/mirror or Map qualification.')
    core.write(staging/'receipt.json', receipt)
    with core._migration_lock():
        _verify_base(candidate)
        if destination.exists(): raise ValueError('corner_configuration_concurrent_install')
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging.rename(destination)
        reference = _artifact(destination/'receipt.json')
        try:
            if reference not in corners.verified_receipts(candidate['moduleId'], candidate['baseDocumentSha256'], candidate['baseContentVersion']):
                raise ValueError('installed_corner_configuration_readback_missing')
        except BaseException:
            # Restore the failed staging packet, leaving all original/base data.
            destination.rename(staging)
            raise
    return dict(configurationId=configuration_id, receipt=reference, alreadyInstalled=False,
        nativePrograms=len(core.read(destination/'load-evidence/index.json')['executions']))


def _full_attempt_bound(cases, doc):
    from . import physics
    # Existing evaluate(): 12 clean trials for dynamic actors, one otherwise,
    # plus 12 mild and 12 moderate, once for calibration and once for holdout.
    quality = sum(2*((12 if any(case.get(k) for k in ('moving_platforms','enemies','saws')) else 1)+24)
                  for case in cases)
    return quality+len(physics.seam_cases(cases[0], doc))+2*len(cases)+sum(len(physics.counter_cases(c))for c in cases)


def qualify(name, workers=2):
    """Use unchanged fixed gates/holdout guard, then actual native admission."""
    from . import physics, holdout_guard, pool_protocols
    if workers not in (1,2): raise ValueError('corner_quality_workers_must_be_one_or_two')
    state, _ = _paths(name); frozen = core.read(state/'frozen-inputs.json')
    core.verify_artifacts([frozen['plan'], frozen['preparation']])
    diagnostics = core.read(state/'preflight.json'); target = state/'qualification.json'
    outcome = core.read(target) if target.exists() else dict(schema='pcg/corner-batch-qualification/v2',
        name=name, frozenInputs=_artifact(state/'frozen-inputs.json'), rows=[], humanReview='UNKNOWN')
    completed = {r['key'] for r in outcome['rows']}; by_key = {r['key']:r for r in frozen['rows']}
    registered = []
    # Registration order is deterministic even when execution uses two workers.
    for diagnostic in sorted(diagnostics['rows'], key=lambda r:r['key']):
        if diagnostic['status']!='preflight_passed' or diagnostic['key'] in completed: continue
        candidate = by_key[diagnostic['key']]
        experiment = _run_name(name, 'full', candidate['key'])
        report_path = core.REPO/'pcg/results'/experiment/'migration-physics.json'
        row = dict(key=candidate['key'], moduleId=candidate['moduleId'], portId=candidate['portId'],
            corner=candidate['corner'], status='tooling_gap', actualAttempts=0)
        try:
            _verify_base(candidate); folder = _verify_prepared(candidate, allow_certified=report_path.exists())
            core.verify_artifacts([diagnostic['report'], diagnostic['replayCases']])
            if not report_path.exists():
                if report_path.parent.exists():
                    raise ValueError('interrupted_corner_quality_preserved_not_rerun')
                local_budget = min(core.read(folder/'corner-protocol.json')['maximumAttempts'],
                    core.read(physics.FULL_PROTOCOL)['maximumAttemptsPerModule'])
                bound = _full_attempt_bound(core.read(folder/'cases.json')['cases'],core.read(folder/'module.mapnote.json'))
                if bound > local_budget:
                    row.update(status='preregistered_budget_gap', maximumRequiredAttempts=bound, fixedMaximumAttempts=local_budget)
                    outcome['rows'].append(row); _save(target,outcome)
                    continue
                try:
                    holdout_guard.check(folder, protocol_path=physics.FULL_PROTOCOL)
                except holdout_guard.HoldoutConflict:
                    holdout_guard.register_pool(folder, _run_name(name, 'pool', candidate['key']))
                protocol = pool_protocols.runtime_protocol(folder,
                    None if core.read(folder/'migration.json').get('holdoutPool') else physics.FULL_PROTOCOL,new_run=True)
                holdout_guard.check(folder, protocol_path=protocol)
            registered.append((candidate, diagnostic, experiment, report_path, row))
        except holdout_guard.HoldoutConflict as error:
            row.update(status='holdout_pool_locked', conflict=error.details)
        except Exception as error:
            row.update(status='holdout_pool_locked' if 'pool' in str(error) or 'holdout' in str(error) else 'tooling_gap', conflict=str(error))
        if not registered or registered[-1][-1] is not row:
            outcome['rows'].append(row); _save(target, outcome)
    def execute(job):
        candidate, diagnostic, experiment, report_path, row = job
        try:
            folder = core.REPO/candidate['prepared']
            if report_path.exists(): report = core.read(report_path)
            else:
                protocol = pool_protocols.runtime_protocol(folder,
                    None if core.read(folder/'migration.json').get('holdoutPool') else physics.FULL_PROTOCOL,new_run=True)
                report = physics.run(folder, experiment, protocol_path=protocol)
            holdout_guard.observe_report(folder, report_path)
            row.update(actualAttempts=report['actualAttempts'], physicsReport=_artifact(report_path))
            local_budget=min(core.read(folder/'corner-protocol.json')['maximumAttempts'],
                core.read(physics.FULL_PROTOCOL)['maximumAttemptsPerModule'])
            if report['actualAttempts']>local_budget:
                row.update(status='fixed_quality_budget_exceeded',fixedMaximumAttempts=local_budget)
            elif not report['passed']:
                row['status'] = 'quality_failed'
            else:
                installed = install_configuration(candidate, diagnostic, report_path, name)
                row.update(status='verified', **installed)
        except holdout_guard.HoldoutConflict as error:
            row.update(status='holdout_pool_locked', conflict=error.details)
        except Exception as error:
            row.update(status='tooling_gap', conflict=str(error), actualAttempts=_attempts(report_path.parent))
        return row
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for future in as_completed([pool.submit(execute,job) for job in registered]):
            row = future.result(); outcome['rows'].append(row); outcome['rows'].sort(key=lambda r:r['key'])
            _save(target, outcome)
            print(json.dumps(row,ensure_ascii=False),flush=True)
            if outcome['actualAttempts']+diagnostics['actualAttempts'] > core.read(state/'plan.json')['maximumAttempts']:
                raise ValueError('frozen_corner_batch_attempt_budget_exceeded')
    outcome['availablePassedProcessed'] = len(outcome['rows']) == sum(r['status']=='preflight_passed' for r in diagnostics['rows'])
    outcome['preflightComplete'] = diagnostics.get('complete',False)
    outcome['complete'] = outcome['availablePassedProcessed'] and outcome['preflightComplete']
    _save(target, outcome)
    return outcome


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    p = commands.add_parser('prepare'); p.add_argument('--name', required=True); p.add_argument('--adapter', choices=('v2','v3','v4'), default='v2'); p.add_argument('--include-certified', action='store_true'); p.add_argument('--only-key',action='append')
    p = commands.add_parser('preflight'); p.add_argument('--name', required=True); p.add_argument('--workers', type=int, default=2); p.add_argument('--only-key', action='append')
    p = commands.add_parser('qualify'); p.add_argument('--name', required=True); p.add_argument('--workers', type=int, default=2)
    args = parser.parse_args()
    if args.command=='prepare': result=prepare(args.name,adapter_version=args.adapter,include_certified=args.include_certified,only_keys=args.only_key)
    elif args.command=='preflight': result=preflight(args.name,args.workers,args.only_key)
    else: result=qualify(args.name,args.workers)
    print(json.dumps({k:v for k,v in result.items() if k!='rows'}, ensure_ascii=False))


if __name__ == '__main__': main()
