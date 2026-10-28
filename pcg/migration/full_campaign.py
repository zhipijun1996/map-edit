"""Inventory-driven migration. Preparation and clean playback never certify content."""
from __future__ import annotations
import collections
from pathlib import Path
from . import core, holdout_guard, pool_protocols


def generated_sources():
    sources = {core.relative(p.parent) for p in core.LEGACY.glob('*/record.json')}
    sources.update(source for source, row in core.ledger()['entries'].items()
                   if row.get('migrationStatus') == 'active'
                   and (core.REPO/source).parent == core.LEGACY)
    return sorted(sources)


def run(name='foundation-full-v4', stage='complete'):
    from . import physics
    core.safe_id(name)
    if stage not in ('prepare', 'clean', 'complete'):
        raise ValueError('unknown_full_migration_stage')
    path = core.STATE/'campaigns'/(name+'.json')
    plan = generated_sources()
    state = core.read(path) if path.exists() else dict(
        schema='pcg/full-module-migration/v1', plan=plan, rows=[],
        policy='All inventoried sources; tooling gaps are implementation work, not disposal.',
        newGameplayFamilies=0, humanApproval='UNKNOWN')
    if state['plan'] != plan:
        raise ValueError('full_campaign_inventory_changed')
    with core.batch_enrollment():
        for source in plan:
            entry = core.ledger()['entries'].get(source, {})
            prefix = Path(source).name
            row = dict(source=source, stage=stage, status='pending', actualAttempts=0)
            prepared = core.REPO/'.cache/migration'/name/prefix
            ready = prepared.parent/(prefix+'-ready')
            experiment = name+'-'+prefix[:12]
            clean_path = core.REPO/'pcg/results'/(experiment+'-clean')/'clean-preflight.json'
            report_path = core.REPO/'pcg/results'/(experiment+'-physics')/'migration-physics.json'
            try:
                if entry.get('migrationStatus') == 'active':
                    core.validate(core.REPO/entry['destination'], require_certified=True)
                    row.update(status='active', moduleId=entry['moduleId'], reused=True)
                else:
                    if not prepared.exists():
                        result = core.prepare(core.REPO/source, prepared)
                        if result['status'] != 'prepared_unverified':
                            raise ValueError(str(result))
                    checked = core.validate(prepared)
                    from .godot_package import audit_cases
                    audit_cases(core.read(prepared/'module.mapnote.json'), core.read(prepared/'cases.json')['cases'], require_replay=False)
                    row.update(status='prepared_unverified', moduleId=checked['moduleId'],
                               prepared=core.relative(prepared), contentVersion=checked['contentVersion'])
                    if stage != 'prepare':
                        clean = core.read(clean_path) if clean_path.exists() else physics.run_clean(prepared,experiment+'-clean')
                        row.update(status='clean_passed' if clean['passed'] else 'repair_required',
                                   cleanReport=core.relative(clean_path), actualAttempts=clean['actualAttempts'])
                        if stage == 'complete' and clean['passed']:
                            if report_path.exists():
                                report=core.read(report_path)
                            else:
                                protocol_path=pool_protocols.runtime_protocol(prepared,new_run=True)
                                holdout_guard.check(prepared,protocol_path=protocol_path)
                                report=physics.run(prepared,experiment+'-physics',protocol_path=protocol_path)
                            holdout_guard.observe_report(prepared,report_path)
                            row['actualAttempts'] += report['actualAttempts']
                            row['physicsReport'] = core.relative(report_path)
                            if not report['passed']:
                                row['status'] = 'physics_failed'
                            else:
                                core.certify(prepared,report_path)
                                if not ready.exists():
                                    core.package(prepared,ready)
                                result = core.promote(ready)
                                row.update(status='active', moduleId=result['moduleId'], reused=False)
            except holdout_guard.HoldoutConflict as error:
                row.update(status='holdout_pool_locked',phase='holdout_guard',conflict=error.details)
            except Exception as error:
                row.update(status='repair_required', conflict=str(error))
            state['rows'] = [r for r in state['rows'] if r['source'] != source] + [row]
            state['counts'] = dict(collections.Counter(r['status'] for r in state['rows']))
            state['actualAttempts'] = sum(r['actualAttempts'] for r in state['rows'])
            state['processedSources'] = len(state['rows'])
            state['inventorySources'] = len(plan)
            core.write(path,state)
            print(__import__('json').dumps(row,ensure_ascii=False),flush=True)
    return state
